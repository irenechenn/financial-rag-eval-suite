from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from financial_rag_eval.datasets import load_cases, load_qrels, load_retrieval_run
from financial_rag_eval.reports import build_report_from_results, write_json_report, write_markdown_report
from financial_rag_eval.schemas import (
    CaseMetricResult,
    EvalCase,
    EvalReport,
    QrelJudgment,
    RetrievedChunk,
    RetrievalRunCase,
)


def build_qrels_report(
    cases: list[EvalCase],
    runs: list[RetrievalRunCase],
    qrels: list[QrelJudgment],
    k: int,
    judgment_statuses: set[str],
) -> EvalReport:
    cases_by_id = {case.id: case for case in cases}
    qrels_by_case = _qrels_by_case(qrels, judgment_statuses)
    results: list[CaseMetricResult] = []

    for run in runs:
        case = cases_by_id.get(run.case_id)
        if case is None:
            raise ValueError(f"Run references unknown case_id: {run.case_id}")

        relevant_ids = qrels_by_case.get(run.case_id, set())
        top_k = sorted(run.retrieved_chunks, key=lambda chunk: chunk.rank)[:k]
        retrieved_ids = {chunk.chunk_id for chunk in top_k}
        covered = sorted(relevant_ids & retrieved_ids)
        missed = sorted(relevant_ids - retrieved_ids)

        results.append(
            CaseMetricResult(
                case_id=case.id,
                category=case.category,
                provider=run.provider,
                k=k,
                precision_at_k=(len(covered) / k) if k > 0 else 0.0,
                recall_at_k=(len(covered) / len(relevant_ids)) if relevant_ids else 0.0,
                hit_at_k=1.0 if covered else 0.0,
                reciprocal_rank_at_k=_reciprocal_rank(top_k, relevant_ids),
                relevant_retrieved=len(covered),
                retrieved_at_k=len(top_k),
                total_relevant=len(relevant_ids),
                covered_targets=covered,
                missed_targets=missed,
                runtime_error=run.runtime_error,
            )
        )

    return build_report_from_results(k=k, case_results=results, label_source=_label_source(judgment_statuses))


def score_qrels_run(
    cases_path: str | Path,
    run_path: str | Path,
    qrels_path: str | Path,
    out_json: str | Path,
    out_md: str | Path,
    k: int,
    judgment_statuses: set[str],
) -> EvalReport:
    report = build_qrels_report(
        cases=load_cases(cases_path),
        runs=load_retrieval_run(run_path),
        qrels=load_qrels(qrels_path),
        k=k,
        judgment_statuses=judgment_statuses,
    )
    write_json_report(report, out_json)
    write_markdown_report(report, out_md)
    return report


def _qrels_by_case(qrels: list[QrelJudgment], statuses: set[str]) -> dict[str, set[str]]:
    grouped: dict[str, set[str]] = defaultdict(set)
    for judgment in qrels:
        if judgment.status in statuses and judgment.relevance > 0:
            grouped[judgment.case_id].add(judgment.chunk_id)
    return grouped


def _reciprocal_rank(retrieved: list[RetrievedChunk], relevant_ids: set[str]) -> float:
    for chunk in retrieved:
        if chunk.chunk_id in relevant_ids:
            return 1.0 / chunk.rank
    return 0.0


def _label_source(statuses: set[str]) -> str:
    return f"qrels:{','.join(sorted(statuses))}"
