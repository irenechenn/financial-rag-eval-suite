from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from financial_rag_eval.datasets import load_cases, load_qrels, load_retrieval_run
from financial_rag_eval.labeling import _preview_text
from financial_rag_eval.schemas import EvalCase, QrelJudgment, RetrievalRunCase
from financial_rag_eval.qrels import write_qrels_jsonl, write_qrels_markdown


class QrelsReviewItem(BaseModel):
    case_id: str
    question: str
    category: str
    chunk_id: str
    status: str
    relevance: int
    rank: int | None = None
    ticker: str | None = None
    year: int | None = None
    quarter: str | None = None
    matched_targets: list[str] = Field(default_factory=list)
    preview: str = ""
    decision: str = "pending"


class QrelsReviewDecision(BaseModel):
    case_id: str
    chunk_id: str
    decision: str
    confidence: float | None = None
    judge_model: str = ""
    rubric_version: str = ""
    rationale: str = ""


def build_qrels_review_packet(
    cases: list[EvalCase],
    runs: list[RetrievalRunCase],
    qrels: list[QrelJudgment],
    statuses: set[str],
) -> list[QrelsReviewItem]:
    cases_by_id = {case.id: case for case in cases}
    chunks_by_case = {
        run.case_id: {chunk.chunk_id: chunk for chunk in run.retrieved_chunks}
        for run in runs
    }
    items: list[QrelsReviewItem] = []

    for judgment in sorted(qrels, key=lambda item: (item.case_id, item.chunk_id)):
        if judgment.status not in statuses:
            continue

        case = cases_by_id.get(judgment.case_id)
        if case is None:
            continue

        chunk = chunks_by_case.get(judgment.case_id, {}).get(judgment.chunk_id)
        items.append(
            QrelsReviewItem(
                case_id=judgment.case_id,
                question=case.question,
                category=case.category,
                chunk_id=judgment.chunk_id,
                status=judgment.status,
                relevance=judgment.relevance,
                rank=chunk.rank if chunk else None,
                ticker=chunk.ticker if chunk else None,
                year=chunk.year if chunk else None,
                quarter=chunk.quarter if chunk else None,
                matched_targets=judgment.matched_targets,
                preview=_preview_text(chunk.text, limit=360) if chunk else "",
            )
        )

    return items


def write_review_packet_jsonl(items: list[QrelsReviewItem], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as file:
        for item in items:
            file.write(json.dumps(item.model_dump(), ensure_ascii=False, sort_keys=True) + "\n")


def write_review_packet_markdown(items: list[QrelsReviewItem], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_review_packet_markdown(items), encoding="utf-8")


def render_review_packet_markdown(items: list[QrelsReviewItem]) -> str:
    lines = [
        "# Qrels Review Packet",
        "",
        "Use this checklist to convert candidate qrels into reviewed judgments. A candidate should only become `accepted` after the chunk directly supports the matched evidence target.",
        "",
        "## Summary",
        "",
        "| Review Items | Pending | Accepted | Rejected |",
        "|---:|---:|---:|---:|",
        (
            f"| {len(items)} | {sum(1 for item in items if item.decision == 'pending')} | "
            f"{sum(1 for item in items if item.decision == 'accepted')} | "
            f"{sum(1 for item in items if item.decision == 'rejected')} |"
        ),
        "",
        "## Checklist",
        "",
    ]

    current_case = ""
    for item in items:
        if item.case_id != current_case:
            current_case = item.case_id
            lines.extend([
                f"### {item.case_id}",
                "",
                f"**Question:** {item.question}",
                "",
            ])

        lines.extend([
            f"- [ ] `accepted` / [ ] `rejected` - `{item.chunk_id}`",
            f"  - Category: {item.category}",
            f"  - Rank: {_format_optional(item.rank)}",
            f"  - Metadata: {_format_metadata(item)}",
            f"  - Matched targets: {_format_list(item.matched_targets)}",
            f"  - Preview: {item.preview}",
            "",
        ])

    return "\n".join(lines)


def make_review_packet(
    cases_path: str | Path,
    run_path: str | Path,
    qrels_path: str | Path,
    out_jsonl: str | Path,
    out_md: str | Path,
    statuses: set[str],
) -> list[QrelsReviewItem]:
    items = build_qrels_review_packet(
        cases=load_cases(cases_path),
        runs=load_retrieval_run(run_path),
        qrels=load_qrels(qrels_path),
        statuses=statuses,
    )
    write_review_packet_jsonl(items, out_jsonl)
    write_review_packet_markdown(items, out_md)
    return items


def apply_review_decisions(
    qrels_path: str | Path,
    decisions_path: str | Path,
    out_jsonl: str | Path,
    out_md: str | Path,
    source: str,
) -> list[QrelJudgment]:
    qrels = load_qrels(qrels_path)
    decisions = _load_review_decisions(decisions_path)
    decisions_by_pair = {(item.case_id, item.chunk_id): item for item in decisions}

    reviewed: list[QrelJudgment] = []
    for judgment in qrels:
        decision = decisions_by_pair.get((judgment.case_id, judgment.chunk_id))
        if decision is None or decision.decision == "pending":
            reviewed.append(judgment)
            continue
        if decision.decision not in {"accepted", "rejected"}:
            raise ValueError(f"Invalid review decision for {judgment.case_id}/{judgment.chunk_id}: {decision.decision}")

        reviewed.append(
            judgment.model_copy(
                update={
                    "status": decision.decision,
                    "source": source,
                    "notes": _decision_note(decision),
                }
            )
        )

    write_qrels_jsonl(reviewed, out_jsonl)
    write_qrels_markdown(reviewed, out_md)
    return reviewed


def _format_optional(value: object | None) -> str:
    return "-" if value is None else str(value)


def _format_metadata(item: QrelsReviewItem) -> str:
    parts = []
    if item.ticker:
        parts.append(item.ticker)
    if item.year:
        parts.append(str(item.year))
    if item.quarter:
        parts.append(item.quarter)
    return " / ".join(parts) if parts else "-"


def _format_list(values: list[str]) -> str:
    return "; ".join(values) if values else "-"


def _load_review_decisions(path: str | Path) -> list[QrelsReviewDecision]:
    records: list[QrelsReviewDecision] = []
    with Path(path).open("r", encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(QrelsReviewDecision.model_validate(json.loads(stripped)))
            except Exception as exc:  # noqa: BLE001
                raise ValueError(f"Invalid review decision at {path}:{line_number}: {exc}") from exc
    return records


def _decision_note(decision: QrelsReviewDecision) -> str:
    parts = ["Applied from review decision."]
    if decision.judge_model:
        parts.append(f"Judge: {decision.judge_model}.")
    if decision.rubric_version:
        parts.append(f"Rubric: {decision.rubric_version}.")
    if decision.confidence is not None:
        parts.append(f"Confidence: {decision.confidence:.2f}.")
    if decision.rationale:
        parts.append(f"Rationale: {decision.rationale}")
    return " ".join(parts)
