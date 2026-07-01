from financial_rag_eval.compare import compare_reports, render_comparison_markdown
from financial_rag_eval.schemas import CaseMetricResult, EvalReport, ReportSummaryRow


def _case(
    case_id: str,
    category: str,
    provider: str,
    precision: float,
    recall: float,
    hit: float,
    rr: float,
    covered: list[str],
    missed: list[str],
) -> CaseMetricResult:
    return CaseMetricResult(
        case_id=case_id,
        category=category,
        provider=provider,
        k=3,
        precision_at_k=precision,
        recall_at_k=recall,
        hit_at_k=hit,
        reciprocal_rank_at_k=rr,
        relevant_retrieved=len(covered),
        retrieved_at_k=3,
        total_relevant=len(covered) + len(missed),
        covered_targets=covered,
        missed_targets=missed,
    )


def _report(provider: str, case_results: list[CaseMetricResult]) -> EvalReport:
    return EvalReport(
        k=3,
        case_results=case_results,
        summary=[
            ReportSummaryRow(
                provider=provider,
                category="simple",
                cases=len(case_results),
                precision_at_k=sum(case.precision_at_k for case in case_results) / len(case_results),
                recall_at_k=sum(case.recall_at_k for case in case_results) / len(case_results),
                hit_at_k=sum(case.hit_at_k for case in case_results) / len(case_results),
                mrr_at_k=sum(case.reciprocal_rank_at_k for case in case_results) / len(case_results),
                runtime_errors=0,
            )
        ],
    )


def test_compare_reports_tracks_summary_and_case_deltas() -> None:
    baseline = _report(
        "baseline",
        [
            _case(
                "case_1",
                "simple",
                "baseline",
                precision=0.0,
                recall=0.0,
                hit=0.0,
                rr=0.0,
                covered=[],
                missed=["AAPL 2023 services"],
            )
        ],
    )
    candidate = _report(
        "candidate",
        [
            _case(
                "case_1",
                "simple",
                "candidate",
                precision=1 / 3,
                recall=1.0,
                hit=1.0,
                rr=0.5,
                covered=["AAPL 2023 services"],
                missed=[],
            )
        ],
    )

    comparison = compare_reports(baseline, candidate)

    assert comparison.summary_deltas[0].precision_delta == 1 / 3
    assert comparison.summary_deltas[0].recall_delta == 1.0
    assert comparison.summary_deltas[0].hit_delta == 1.0
    assert comparison.summary_deltas[0].mrr_delta == 0.5
    assert comparison.case_deltas[0].status == "improved"
    assert comparison.case_deltas[0].newly_covered_targets == ["AAPL 2023 services"]

    markdown = render_comparison_markdown(comparison)
    assert "Summary Deltas" in markdown
    assert "AAPL 2023 services" in markdown


def test_compare_reports_rejects_different_k_values() -> None:
    baseline = _report("baseline", [_case("case_1", "simple", "baseline", 0, 0, 0, 0, [], ["x"])])
    candidate = _report("candidate", [_case("case_1", "simple", "candidate", 0, 0, 0, 0, [], ["x"])])
    candidate.k = 5

    try:
        compare_reports(baseline, candidate)
    except ValueError as exc:
        assert "different k values" in str(exc)
    else:
        raise AssertionError("Expected ValueError")