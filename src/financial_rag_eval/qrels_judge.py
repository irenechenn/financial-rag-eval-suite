from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel

from financial_rag_eval.datasets import load_cases, load_qrels, load_retrieval_run
from financial_rag_eval.labeling import _criteria_label
from financial_rag_eval.qrels_review import QrelsReviewDecision, build_qrels_review_packet
from financial_rag_eval.schemas import EvalCase, RelevanceTarget

RUBRIC_VERSION = "retrieval-relevance-rubric-v1"
RUBRIC_JUDGE_MODEL = "local-rubric-judge-v1"
CLAUDE_RUBRIC_VERSION = "claude-relevance-rubric-v1"
DEFAULT_CLAUDE_JUDGE_MODEL = "claude-sonnet-5"
ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"

TERM_ALIASES = {
    "advertising": ["advertising", "advertiser", "advertisers", "ads", "ad demand"],
    "aws": ["aws", "trainium", "inferentia", "codewhisperer", "cloud"],
    "azure": ["azure", "azure ai", "azure openai"],
    "cloud": ["cloud", "azure", "public cloud"],
    "margin": ["margin", "margins", "gross margin", "profitability"],
    "profitability": ["profitability", "profit", "operating income", "margin"],
    "services": ["services"],
    "revenue": ["revenue", "sales"],
    "data": ["data"],
    "center": ["center", "centers"],
}


class JudgeRubric(BaseModel):
    version: str = RUBRIC_VERSION
    accept_rule: str
    reject_rule: str
    confidence_policy: str


class AnthropicTransport(Protocol):
    def complete(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Return one Anthropic Messages API response."""


class AnthropicMessagesClient:
    def __init__(self, api_key: str, timeout_seconds: int = 60) -> None:
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def complete(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            ANTHROPIC_MESSAGES_URL,
            data=body,
            method="POST",
            headers={
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
                "x-api-key": self.api_key,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            message = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Anthropic API request failed with HTTP {exc.code}: {message}") from exc


def default_rubric() -> JudgeRubric:
    return JudgeRubric(
        accept_rule=(
            "Accept only when the chunk preview directly supports the matched evidence target, "
            "including required topic terms and the expected company/year metadata."
        ),
        reject_rule=(
            "Reject call openers, logistics, unrelated financial discussion, or chunks that only "
            "match ticker/year without supporting the target topic."
        ),
        confidence_policy=(
            "Use high confidence for direct term and topic support, medium for partial support, "
            "and low for boilerplate or unrelated text."
        ),
    )


def judge_qrels_with_rubric(
    cases: list[EvalCase],
    runs,
    qrels,
    statuses: set[str],
) -> list[QrelsReviewDecision]:
    items = build_qrels_review_packet(cases=cases, runs=runs, qrels=qrels, statuses=statuses)
    targets_by_case = _targets_by_case(cases)
    decisions: list[QrelsReviewDecision] = []

    for item in items:
        required_terms = _required_terms_for_item(targets_by_case.get(item.case_id, {}), item.matched_targets)
        preview = item.preview.lower()
        missing_terms = [term for term in required_terms if not _term_supported(term, preview)]
        is_boilerplate = _looks_like_boilerplate(preview)

        if required_terms and not missing_terms and not is_boilerplate:
            decision = "accepted"
            confidence = 0.85
            rationale = "Preview contains the required target terms and is not call-opening boilerplate."
        elif is_boilerplate:
            decision = "rejected"
            confidence = 0.9
            rationale = "Preview appears to be call-opening or logistics text rather than evidence."
        else:
            decision = "rejected"
            confidence = 0.75
            missing = ", ".join(missing_terms) if missing_terms else "direct target evidence"
            rationale = f"Preview does not directly support the matched target; missing {missing}."

        decisions.append(
            QrelsReviewDecision(
                case_id=item.case_id,
                chunk_id=item.chunk_id,
                decision=decision,
                confidence=confidence,
                judge_model=RUBRIC_JUDGE_MODEL,
                rubric_version=RUBRIC_VERSION,
                rationale=rationale,
            )
        )

    return decisions


def judge_qrels_with_claude(
    cases: list[EvalCase],
    runs,
    qrels,
    statuses: set[str],
    model: str,
    client: AnthropicTransport,
) -> list[QrelsReviewDecision]:
    items = build_qrels_review_packet(cases=cases, runs=runs, qrels=qrels, statuses=statuses)
    decisions: list[QrelsReviewDecision] = []

    for item in items:
        payload = _claude_payload(item=item, model=model)
        response = client.complete(payload)
        parsed = _parse_claude_decision(response)
        decisions.append(
            QrelsReviewDecision(
                case_id=item.case_id,
                chunk_id=item.chunk_id,
                decision=parsed["decision"],
                confidence=parsed["confidence"],
                judge_model=model,
                rubric_version=CLAUDE_RUBRIC_VERSION,
                rationale=parsed["rationale"],
            )
        )

    return decisions


def write_judge_decisions_jsonl(decisions: list[QrelsReviewDecision], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as file:
        for decision in decisions:
            file.write(json.dumps(decision.model_dump(), ensure_ascii=False, sort_keys=True) + "\n")


def write_judge_decisions_markdown(decisions: list[QrelsReviewDecision], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_judge_decisions_markdown(decisions), encoding="utf-8")


def render_judge_decisions_markdown(decisions: list[QrelsReviewDecision]) -> str:
    accepted = sum(1 for item in decisions if item.decision == "accepted")
    rejected = sum(1 for item in decisions if item.decision == "rejected")
    judge_model = decisions[0].judge_model if decisions else "-"
    rubric_version = decisions[0].rubric_version if decisions else "-"
    lines = [
        "# Qrels Judge Decisions",
        "",
        "These decisions were produced by an independent qrels judge. They are useful for exercising the judge-review workflow and should be spot-checked before being treated as production benchmark labels.",
        "",
        "## Rubric",
        "",
        f"| Version | `{rubric_version}` |",
        "|---|---|",
        f"| Judge model | `{judge_model}` |",
        "",
        "## Summary",
        "",
        "| Decisions | Accepted | Rejected |",
        "|---:|---:|---:|",
        f"| {len(decisions)} | {accepted} | {rejected} |",
        "",
        "## Decisions",
        "",
        "| Case | Chunk ID | Decision | Confidence | Rationale |",
        "|---|---|---|---:|---|",
    ]
    for decision in decisions:
        lines.append(
            f"| {decision.case_id} | `{decision.chunk_id}` | {decision.decision} | "
            f"{_format_confidence(decision.confidence)} | {decision.rationale} |"
        )
    lines.append("")
    return "\n".join(lines)


def judge_qrels(
    cases_path: str | Path,
    run_path: str | Path,
    qrels_path: str | Path,
    out_jsonl: str | Path,
    out_md: str | Path,
    statuses: set[str],
    provider: str = "rubric",
    model: str | None = None,
) -> list[QrelsReviewDecision]:
    cases = load_cases(cases_path)
    runs = load_retrieval_run(run_path)
    qrels = load_qrels(qrels_path)

    if provider == "rubric":
        decisions = judge_qrels_with_rubric(cases=cases, runs=runs, qrels=qrels, statuses=statuses)
    elif provider == "claude":
        selected_model = model or _env_value("ANTHROPIC_MODEL") or DEFAULT_CLAUDE_JUDGE_MODEL
        decisions = judge_qrels_with_claude(
            cases=cases,
            runs=runs,
            qrels=qrels,
            statuses=statuses,
            model=selected_model,
            client=AnthropicMessagesClient(api_key=_anthropic_api_key()),
        )
    else:
        raise ValueError(f"Unsupported judge provider: {provider}")

    write_judge_decisions_jsonl(decisions, out_jsonl)
    write_judge_decisions_markdown(decisions, out_md)
    return decisions


def _claude_payload(item, model: str) -> dict[str, Any]:
    prompt = f"""
You are an independent retrieval relevance judge for a financial RAG evaluation suite.

Decide whether the retrieved transcript chunk directly supports the matched evidence target.

Rubric:
- Accept only if the chunk provides direct evidence for the matched target.
- Reject call-opening boilerplate, event logistics, unrelated financial discussion, or metadata-only matches.
- Prefer semantic relevance over exact keyword matching when the financial concept is clearly equivalent.
- Return JSON only with keys: decision, confidence, rationale.
- decision must be "accepted" or "rejected".
- confidence must be a number from 0.0 to 1.0.
- rationale must be one concise sentence.

Question:
{item.question}

Case category:
{item.category}

Chunk metadata:
ticker={item.ticker or ""}
year={item.year or ""}
quarter={item.quarter or ""}
rank={item.rank or ""}

Matched targets:
{", ".join(item.matched_targets)}

Chunk preview:
{item.preview}
""".strip()
    return {
        "model": model,
        "max_tokens": 400,
        "messages": [{"role": "user", "content": prompt}],
    }


def _parse_claude_decision(response: dict[str, Any]) -> dict[str, Any]:
    text_parts = [
        block.get("text", "")
        for block in response.get("content", [])
        if block.get("type") == "text"
    ]
    raw_text = "\n".join(text_parts).strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.lower().startswith("json"):
            raw_text = raw_text[4:].strip()
    data = json.loads(raw_text)
    decision = data.get("decision")
    if decision not in {"accepted", "rejected"}:
        raise ValueError(f"Invalid Claude judge decision: {decision}")
    confidence = float(data.get("confidence", 0.0))
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(f"Invalid Claude judge confidence: {confidence}")
    rationale = str(data.get("rationale", "")).strip()
    return {"decision": decision, "confidence": confidence, "rationale": rationale}


def _anthropic_api_key() -> str:
    api_key = _env_value("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is required for --judge-provider claude")
    return api_key


def _env_value(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    env_path = Path(".env")
    if not env_path.exists():
        return ""
    with env_path.open("r", encoding="utf-8-sig") as file:
        for line in file:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            if key.strip() == name:
                return value.strip().strip('"').strip("'")
    return ""


def _targets_by_case(cases: list[EvalCase]) -> dict[str, dict[str, RelevanceTarget]]:
    output: dict[str, dict[str, RelevanceTarget]] = {}
    for case in cases:
        output[case.id] = {
            _criteria_label(target, index): target
            for index, target in enumerate(case.relevance_targets, start=1)
        }
    return output


def _required_terms_for_item(
    targets: dict[str, RelevanceTarget],
    matched_targets: list[str],
) -> list[str]:
    terms: list[str] = []
    for label in matched_targets:
        target = targets.get(label)
        if target:
            terms.extend(target.required_terms)
    return sorted(set(terms))


def _looks_like_boilerplate(preview: str) -> bool:
    boilerplate_terms = [
        "conference operator",
        "listen-only mode",
        "operator instructions",
        "conference call",
        "being recorded",
        "turn the conference over",
    ]
    return any(term in preview for term in boilerplate_terms)


def _term_supported(term: str, preview: str) -> bool:
    aliases = TERM_ALIASES.get(term.lower(), [term.lower()])
    return any(alias in preview for alias in aliases)


def _format_confidence(confidence: float | None) -> str:
    if confidence is None:
        return "-"
    return f"{confidence:.2f}"
