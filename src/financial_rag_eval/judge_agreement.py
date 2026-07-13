from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from financial_rag_eval.qrels_review import QrelsReviewDecision


class JudgeDecisionDelta(BaseModel):
    case_id: str
    chunk_id: str
    baseline_decision: str
    candidate_decision: str
    baseline_confidence: float | None = None
    candidate_confidence: float | None = None
    baseline_rationale: str = ""
    candidate_rationale: str = ""


class JudgeAgreementReport(BaseModel):
    baseline_name: str
    candidate_name: str
    shared_decisions: int
    agreements: int
    disagreements: int
    agreement_rate: float
    baseline_only: list[str] = Field(default_factory=list)
    candidate_only: list[str] = Field(default_factory=list)
    deltas: list[JudgeDecisionDelta] = Field(default_factory=list)


def load_review_decisions(path: str | Path) -> list[QrelsReviewDecision]:
    records: list[QrelsReviewDecision] = []
    with Path(path).open("r", encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(QrelsReviewDecision.model_validate(json.loads(stripped)))
            except Exception as exc:  # noqa: BLE001
                raise ValueError(f"Invalid judge decision at {path}:{line_number}: {exc}") from exc
    return records


def compare_judge_decisions(
    baseline: list[QrelsReviewDecision],
    candidate: list[QrelsReviewDecision],
    baseline_name: str,
    candidate_name: str,
) -> JudgeAgreementReport:
    baseline_by_key = {(item.case_id, item.chunk_id): item for item in baseline}
    candidate_by_key = {(item.case_id, item.chunk_id): item for item in candidate}
    shared_keys = sorted(set(baseline_by_key) & set(candidate_by_key))

    deltas: list[JudgeDecisionDelta] = []
    agreements = 0
    for key in shared_keys:
        baseline_item = baseline_by_key[key]
        candidate_item = candidate_by_key[key]
        if baseline_item.decision == candidate_item.decision:
            agreements += 1
            continue
        deltas.append(
            JudgeDecisionDelta(
                case_id=key[0],
                chunk_id=key[1],
                baseline_decision=baseline_item.decision,
                candidate_decision=candidate_item.decision,
                baseline_confidence=baseline_item.confidence,
                candidate_confidence=candidate_item.confidence,
                baseline_rationale=baseline_item.rationale,
                candidate_rationale=candidate_item.rationale,
            )
        )

    shared = len(shared_keys)
    disagreements = len(deltas)
    return JudgeAgreementReport(
        baseline_name=baseline_name,
        candidate_name=candidate_name,
        shared_decisions=shared,
        agreements=agreements,
        disagreements=disagreements,
        agreement_rate=(agreements / shared) if shared else 0.0,
        baseline_only=[_format_key(key) for key in sorted(set(baseline_by_key) - set(candidate_by_key))],
        candidate_only=[_format_key(key) for key in sorted(set(candidate_by_key) - set(baseline_by_key))],
        deltas=deltas,
    )


def write_agreement_json(report: JudgeAgreementReport, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report.model_dump(), indent=2, sort_keys=True), encoding="utf-8")


def write_agreement_markdown(report: JudgeAgreementReport, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_agreement_markdown(report), encoding="utf-8")


def render_agreement_markdown(report: JudgeAgreementReport) -> str:
    lines = [
        "# Judge Agreement Report",
        "",
        "This report compares relevance decisions from two qrels judges over the same pooled judgments.",
        "",
        "## Summary",
        "",
        "| Baseline | Candidate | Shared Decisions | Agreements | Disagreements | Agreement Rate |",
        "|---|---|---:|---:|---:|---:|",
        (
            f"| {report.baseline_name} | {report.candidate_name} | {report.shared_decisions} | "
            f"{report.agreements} | {report.disagreements} | {report.agreement_rate:.3f} |"
        ),
        "",
        "## Disagreements",
        "",
        "| Case | Chunk ID | Baseline | Candidate | Baseline Rationale | Candidate Rationale |",
        "|---|---|---|---|---|---|",
    ]
    if report.deltas:
        for delta in report.deltas:
            lines.append(
                f"| {delta.case_id} | `{delta.chunk_id}` | {delta.baseline_decision} | "
                f"{delta.candidate_decision} | {_escape_cell(delta.baseline_rationale)} | "
                f"{_escape_cell(delta.candidate_rationale)} |"
            )
    else:
        lines.append("| _None_ |  |  |  |  |  |")

    lines.extend([
        "",
        "## Coverage",
        "",
        "| Check | Values |",
        "|---|---|",
        f"| Baseline-only decisions | {_format_list(report.baseline_only)} |",
        f"| Candidate-only decisions | {_format_list(report.candidate_only)} |",
        "",
    ])
    return "\n".join(lines)


def compare_judge_files(
    baseline_path: str | Path,
    candidate_path: str | Path,
    baseline_name: str,
    candidate_name: str,
    out_json: str | Path,
    out_md: str | Path,
) -> JudgeAgreementReport:
    report = compare_judge_decisions(
        baseline=load_review_decisions(baseline_path),
        candidate=load_review_decisions(candidate_path),
        baseline_name=baseline_name,
        candidate_name=candidate_name,
    )
    write_agreement_json(report, out_json)
    write_agreement_markdown(report, out_md)
    return report


def _format_key(key: tuple[str, str]) -> str:
    return f"{key[0]}::{key[1]}"


def _format_list(values: list[str]) -> str:
    return "; ".join(values) if values else "_None_"


def _escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
