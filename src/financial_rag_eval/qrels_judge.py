from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from financial_rag_eval.datasets import load_cases, load_qrels, load_retrieval_run
from financial_rag_eval.labeling import _criteria_label
from financial_rag_eval.qrels_review import QrelsReviewDecision, build_qrels_review_packet
from financial_rag_eval.schemas import EvalCase, RelevanceTarget

RUBRIC_VERSION = "retrieval-relevance-rubric-v1"
RUBRIC_JUDGE_MODEL = "local-rubric-judge-v1"

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
    lines = [
        "# Qrels Judge Decisions",
        "",
        "These decisions were produced by a local rubric judge. They are useful for exercising the judge-review workflow and should be spot-checked before being treated as final benchmark labels.",
        "",
        "## Rubric",
        "",
        f"| Version | `{RUBRIC_VERSION}` |",
        "|---|---|",
        f"| Judge model | `{RUBRIC_JUDGE_MODEL}` |",
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
) -> list[QrelsReviewDecision]:
    decisions = judge_qrels_with_rubric(
        cases=load_cases(cases_path),
        runs=load_retrieval_run(run_path),
        qrels=load_qrels(qrels_path),
        statuses=statuses,
    )
    write_judge_decisions_jsonl(decisions, out_jsonl)
    write_judge_decisions_markdown(decisions, out_md)
    return decisions


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
