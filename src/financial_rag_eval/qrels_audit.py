from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from pydantic import BaseModel, Field

from financial_rag_eval.datasets import load_cases, load_qrels
from financial_rag_eval.schemas import EvalCase, QrelJudgment


class QrelsCategoryCoverage(BaseModel):
    category: str
    cases: int
    cases_with_qrels: int
    judgments: int


class QrelsAuditReport(BaseModel):
    total_cases: int
    total_judgments: int
    status_counts: dict[str, int] = Field(default_factory=dict)
    relevance_counts: dict[int, int] = Field(default_factory=dict)
    source_counts: dict[str, int] = Field(default_factory=dict)
    category_coverage: list[QrelsCategoryCoverage] = Field(default_factory=list)
    unknown_case_ids: list[str] = Field(default_factory=list)
    duplicate_judgments: list[str] = Field(default_factory=list)
    unlabeled_case_ids: list[str] = Field(default_factory=list)


def build_qrels_audit(cases: list[EvalCase], qrels: list[QrelJudgment]) -> QrelsAuditReport:
    cases_by_id = {case.id: case for case in cases}
    qrels_by_case: dict[str, list[QrelJudgment]] = defaultdict(list)
    pair_counts: Counter[tuple[str, str]] = Counter()

    for judgment in qrels:
        qrels_by_case[judgment.case_id].append(judgment)
        pair_counts[(judgment.case_id, judgment.chunk_id)] += 1

    category_cases: dict[str, list[EvalCase]] = defaultdict(list)
    for case in cases:
        category_cases[case.category].append(case)

    category_coverage: list[QrelsCategoryCoverage] = []
    for category, category_case_list in sorted(category_cases.items()):
        category_case_ids = {case.id for case in category_case_list}
        judgments = [judgment for judgment in qrels if judgment.case_id in category_case_ids]
        category_coverage.append(
            QrelsCategoryCoverage(
                category=category,
                cases=len(category_case_list),
                cases_with_qrels=sum(1 for case_id in category_case_ids if qrels_by_case.get(case_id)),
                judgments=len(judgments),
            )
        )

    return QrelsAuditReport(
        total_cases=len(cases),
        total_judgments=len(qrels),
        status_counts=dict(sorted(Counter(judgment.status for judgment in qrels).items())),
        relevance_counts=dict(sorted(Counter(judgment.relevance for judgment in qrels).items())),
        source_counts=dict(sorted(Counter(judgment.source or "unknown" for judgment in qrels).items())),
        category_coverage=category_coverage,
        unknown_case_ids=sorted({judgment.case_id for judgment in qrels if judgment.case_id not in cases_by_id}),
        duplicate_judgments=[
            f"{case_id}::{chunk_id}"
            for (case_id, chunk_id), count in sorted(pair_counts.items())
            if count > 1
        ],
        unlabeled_case_ids=sorted(case.id for case in cases if not qrels_by_case.get(case.id)),
    )


def write_qrels_audit_json(report: QrelsAuditReport, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report.model_dump(), indent=2, sort_keys=True), encoding="utf-8")


def write_qrels_audit_markdown(report: QrelsAuditReport, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_qrels_audit_markdown(report), encoding="utf-8")


def render_qrels_audit_markdown(report: QrelsAuditReport) -> str:
    lines = [
        "# Qrels Audit Report",
        "",
        "This report validates pooled relevance judgments before they are used as gold labels.",
        "",
        "## Summary",
        "",
        "| Total Cases | Total Judgments | Unknown Case IDs | Duplicate Judgments | Unlabeled Cases |",
        "|---:|---:|---:|---:|---:|",
        (
            f"| {report.total_cases} | {report.total_judgments} | "
            f"{len(report.unknown_case_ids)} | {len(report.duplicate_judgments)} | "
            f"{len(report.unlabeled_case_ids)} |"
        ),
        "",
        "## Status Counts",
        "",
        "| Status | Judgments |",
        "|---|---:|",
    ]
    for status, count in report.status_counts.items():
        lines.append(f"| {status} | {count} |")

    lines.extend([
        "",
        "## Relevance Counts",
        "",
        "| Relevance | Judgments |",
        "|---:|---:|",
    ])
    for relevance, count in report.relevance_counts.items():
        lines.append(f"| {relevance} | {count} |")

    lines.extend([
        "",
        "## Category Coverage",
        "",
        "| Category | Cases | Cases With Qrels | Judgments |",
        "|---|---:|---:|---:|",
    ])
    for row in report.category_coverage:
        lines.append(f"| {row.category} | {row.cases} | {row.cases_with_qrels} | {row.judgments} |")

    lines.extend([
        "",
        "## Sources",
        "",
        "| Source | Judgments |",
        "|---|---:|",
    ])
    for source, count in report.source_counts.items():
        lines.append(f"| {source} | {count} |")

    lines.extend([
        "",
        "## Unlabeled Cases",
        "",
        "| Case ID |",
        "|---|",
    ])
    if report.unlabeled_case_ids:
        for case_id in report.unlabeled_case_ids:
            lines.append(f"| {case_id} |")
    else:
        lines.append("| _None_ |")

    lines.extend([
        "",
        "## Integrity Issues",
        "",
        "| Check | Values |",
        "|---|---|",
        f"| Unknown case IDs | {_format_list(report.unknown_case_ids)} |",
        f"| Duplicate judgments | {_format_list(report.duplicate_judgments)} |",
        "",
    ])
    return "\n".join(lines)


def audit_qrels(
    cases_path: str | Path,
    qrels_path: str | Path,
    out_json: str | Path,
    out_md: str | Path,
) -> QrelsAuditReport:
    report = build_qrels_audit(load_cases(cases_path), load_qrels(qrels_path))
    write_qrels_audit_json(report, out_json)
    write_qrels_audit_markdown(report, out_md)
    return report


def _format_list(values: list[str]) -> str:
    if not values:
        return "_None_"
    return "; ".join(values)
