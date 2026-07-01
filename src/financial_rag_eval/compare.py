from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from pydantic import BaseModel, Field

from financial_rag_eval.schemas import CaseMetricResult, EvalReport


class SummaryDelta(BaseModel):
    category: str
    baseline_provider: str
    candidate_provider: str
    cases: int
    precision_delta: float
    recall_delta: float
    hit_delta: float
    mrr_delta: float
    runtime_error_delta: int


class CaseDelta(BaseModel):
    case_id: str
    category: str
    baseline_provider: str
    candidate_provider: str
    precision_delta: float
    recall_delta: float
    hit_delta: float
    mrr_delta: float
    newly_covered_targets: list[str] = Field(default_factory=list)
    newly_missed_targets: list[str] = Field(default_factory=list)
    status: str


class RunComparisonReport(BaseModel):
    baseline_name: str
    candidate_name: str
    k: int
    summary_deltas: list[SummaryDelta]
    case_deltas: list[CaseDelta]


def load_eval_report(path: str | Path) -> EvalReport:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return EvalReport.model_validate(payload)


def compare_reports(
    baseline: EvalReport,
    candidate: EvalReport,
    baseline_name: str = "baseline",
    candidate_name: str = "candidate",
) -> RunComparisonReport:
    if baseline.k != candidate.k:
        raise ValueError(f"Cannot compare reports with different k values: {baseline.k} vs {candidate.k}")

    baseline_cases = {case.case_id: case for case in baseline.case_results}
    candidate_cases = {case.case_id: case for case in candidate.case_results}
    common_ids = sorted(set(baseline_cases) & set(candidate_cases))
    if not common_ids:
        raise ValueError("Reports do not share any case IDs.")

    case_deltas = [
        _case_delta(baseline_cases[case_id], candidate_cases[case_id])
        for case_id in common_ids
    ]

    return RunComparisonReport(
        baseline_name=baseline_name,
        candidate_name=candidate_name,
        k=baseline.k,
        summary_deltas=_summary_deltas(case_deltas),
        case_deltas=case_deltas,
    )


def write_comparison_json(report: RunComparisonReport, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report.model_dump(), indent=2, sort_keys=True), encoding="utf-8")


def write_comparison_markdown(report: RunComparisonReport, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_comparison_markdown(report), encoding="utf-8")


def render_comparison_markdown(report: RunComparisonReport) -> str:
    lines = [
        "# Retrieval Run Comparison",
        "",
        "## Overview",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Baseline | {report.baseline_name} |",
        f"| Candidate | {report.candidate_name} |",
        f"| Metrics | Precision@{report.k}, Recall@{report.k}, Hit@{report.k}, MRR@{report.k} deltas |",
        "",
        "```mermaid",
        "flowchart LR",
        "    A[\"Baseline report\"] --> C[\"Compare metrics\"]",
        "    B[\"Candidate report\"] --> C",
        "    C --> D[\"Summary deltas\"]",
        "    C --> E[\"Case-level regressions\"]",
        "    C --> F[\"Newly covered targets\"]",
        "```",
        "",
        "## Summary Deltas",
        "",
        "Positive values mean the candidate improved over the baseline.",
        "",
        "| Category | Cases | Precision Delta | Recall Delta | Hit Delta | MRR Delta | Runtime Error Delta |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report.summary_deltas:
        lines.append(
            f"| {row.category} | {row.cases} | {row.precision_delta:+.3f} | "
            f"{row.recall_delta:+.3f} | {row.hit_delta:+.3f} | {row.mrr_delta:+.3f} | "
            f"{row.runtime_error_delta:+d} |"
        )

    notable = [case for case in report.case_deltas if case.status != "unchanged"]
    lines.extend([
        "",
        "## Case-Level Changes",
        "",
        "| Case | Category | Status | Precision Delta | Recall Delta | Hit Delta | MRR Delta | Newly Covered | Newly Missed |",
        "|---|---|---|---:|---:|---:|---:|---|---|",
    ])
    if notable:
        for case in notable:
            lines.append(
                f"| {case.case_id} | {case.category} | {case.status} | "
                f"{case.precision_delta:+.3f} | {case.recall_delta:+.3f} | "
                f"{case.hit_delta:+.3f} | {case.mrr_delta:+.3f} | "
                f"{_format_list(case.newly_covered_targets)} | {_format_list(case.newly_missed_targets)} |"
            )
    else:
        lines.append("| _None_ |  |  |  |  |  |  |  |  |")

    lines.append("")
    return "\n".join(lines)


def _case_delta(baseline: CaseMetricResult, candidate: CaseMetricResult) -> CaseDelta:
    newly_covered = sorted(set(candidate.covered_targets) - set(baseline.covered_targets))
    newly_missed = sorted(set(candidate.missed_targets) - set(baseline.missed_targets))
    precision_delta = candidate.precision_at_k - baseline.precision_at_k
    recall_delta = candidate.recall_at_k - baseline.recall_at_k
    hit_delta = candidate.hit_at_k - baseline.hit_at_k
    mrr_delta = candidate.reciprocal_rank_at_k - baseline.reciprocal_rank_at_k
    status = _case_status(precision_delta, recall_delta, hit_delta, mrr_delta, newly_covered, newly_missed)

    return CaseDelta(
        case_id=baseline.case_id,
        category=baseline.category,
        baseline_provider=baseline.provider,
        candidate_provider=candidate.provider,
        precision_delta=precision_delta,
        recall_delta=recall_delta,
        hit_delta=hit_delta,
        mrr_delta=mrr_delta,
        newly_covered_targets=newly_covered,
        newly_missed_targets=newly_missed,
        status=status,
    )


def _case_status(
    precision_delta: float,
    recall_delta: float,
    hit_delta: float,
    mrr_delta: float,
    newly_covered: list[str],
    newly_missed: list[str],
) -> str:
    aggregate = precision_delta + recall_delta + hit_delta + mrr_delta
    if newly_missed and not newly_covered:
        return "regressed"
    if newly_covered and not newly_missed:
        return "improved"
    if aggregate > 1e-9:
        return "improved"
    if aggregate < -1e-9:
        return "regressed"
    return "unchanged"


def _summary_deltas(case_deltas: list[CaseDelta]) -> list[SummaryDelta]:
    grouped: dict[str, list[CaseDelta]] = defaultdict(list)
    for case in case_deltas:
        grouped[case.category].append(case)

    rows: list[SummaryDelta] = []
    for category, group in sorted(grouped.items()):
        cases = len(group)
        rows.append(
            SummaryDelta(
                category=category,
                baseline_provider=group[0].baseline_provider,
                candidate_provider=group[0].candidate_provider,
                cases=cases,
                precision_delta=sum(case.precision_delta for case in group) / cases,
                recall_delta=sum(case.recall_delta for case in group) / cases,
                hit_delta=sum(case.hit_delta for case in group) / cases,
                mrr_delta=sum(case.mrr_delta for case in group) / cases,
                runtime_error_delta=0,
            )
        )
    return rows


def _format_list(values: list[str]) -> str:
    return "; ".join(values) if values else "-"