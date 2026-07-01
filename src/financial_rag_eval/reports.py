from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from financial_rag_eval.metrics import (
    covered_target_labels,
    missed_target_labels,
    precision_at_k,
    recall_at_k,
    relevant_retrieved_at_k,
    total_relevant_count,
)
from financial_rag_eval.schemas import (
    CaseMetricResult,
    EvalCase,
    EvalReport,
    ReportSummaryRow,
    RetrievalRunCase,
)


def build_report(cases: list[EvalCase], runs: list[RetrievalRunCase], k: int) -> EvalReport:
    cases_by_id = {case.id: case for case in cases}
    results: list[CaseMetricResult] = []

    for run in runs:
        case = cases_by_id.get(run.case_id)
        if case is None:
            raise ValueError(f"Run references unknown case_id: {run.case_id}")

        results.append(
            CaseMetricResult(
                case_id=case.id,
                category=case.category,
                provider=run.provider,
                k=k,
                precision_at_k=precision_at_k(run.retrieved_chunks, case, k),
                recall_at_k=recall_at_k(run.retrieved_chunks, case, k),
                relevant_retrieved=relevant_retrieved_at_k(run.retrieved_chunks, case, k),
                retrieved_at_k=min(len(run.retrieved_chunks), k),
                total_relevant=total_relevant_count(case),
                covered_targets=covered_target_labels(run.retrieved_chunks, case, k),
                missed_targets=missed_target_labels(run.retrieved_chunks, case, k),
                runtime_error=run.runtime_error,
            )
        )

    return EvalReport(k=k, case_results=results, summary=_summarize(results))


def _summarize(results: list[CaseMetricResult]) -> list[ReportSummaryRow]:
    grouped: dict[tuple[str, str], list[CaseMetricResult]] = defaultdict(list)
    for result in results:
        grouped[(result.provider, result.category)].append(result)

    rows: list[ReportSummaryRow] = []
    for (provider, category), group in sorted(grouped.items()):
        cases = len(group)
        rows.append(
            ReportSummaryRow(
                provider=provider,
                category=category,
                cases=cases,
                precision_at_k=sum(item.precision_at_k for item in group) / cases,
                recall_at_k=sum(item.recall_at_k for item in group) / cases,
                runtime_errors=sum(1 for item in group if item.runtime_error),
            )
        )
    return rows


def write_json_report(report: EvalReport, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report.model_dump(), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def write_markdown_report(report: EvalReport, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown_report(report), encoding="utf-8")


def render_markdown_report(report: EvalReport) -> str:
    lines = [
        "# Retrieval Evaluation Report",
        "",
        f"Metric: Precision@{report.k} / Recall@{report.k}",
        "",
        "## Benchmark Summary",
        "",
        "| Provider | Case Type | Cases | Precision@K | Recall@K | Runtime Errors |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in report.summary:
        lines.append(
            f"| {row.provider} | {row.category} | {row.cases} | "
            f"{row.precision_at_k:.3f} | {row.recall_at_k:.3f} | {row.runtime_errors} |"
        )

    lines.extend([
        "",
        "## Failure Analysis",
        "",
        "Cases below missed at least one expected evidence target.",
        "",
        "| Case | Provider | Category | Recall@K | Covered Targets | Missed Targets |",
        "|---|---|---|---:|---|---|",
    ])
    failures = [result for result in report.case_results if result.missed_targets or result.runtime_error]
    if failures:
        for result in failures:
            covered = _format_targets(result.covered_targets)
            missed = result.runtime_error or _format_targets(result.missed_targets)
            lines.append(
                f"| {result.case_id} | {result.provider} | {result.category} | "
                f"{result.recall_at_k:.3f} | {covered} | {missed} |"
            )
    else:
        lines.append("| _None_ |  |  |  |  |  |")

    lines.extend([
        "",
        "## Case Results",
        "",
        "| Case | Provider | Category | Precision@K | Recall@K | Relevant Retrieved |",
        "|---|---|---|---:|---:|---:|",
    ])
    for result in report.case_results:
        lines.append(
            f"| {result.case_id} | {result.provider} | {result.category} | "
            f"{result.precision_at_k:.3f} | {result.recall_at_k:.3f} | "
            f"{result.relevant_retrieved}/{result.total_relevant} |"
        )
    lines.append("")
    return "\n".join(lines)


def _format_targets(targets: list[str]) -> str:
    if not targets:
        return "-"
    return "; ".join(targets)