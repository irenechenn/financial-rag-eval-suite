from financial_rag_eval.reports import build_report, render_markdown_report
from financial_rag_eval.schemas import EvalCase, RetrievedChunk, RetrievalRunCase


def test_build_report_groups_by_provider_and_category() -> None:
    cases = [
        EvalCase(id="c1", question="q", category="simple", relevant_chunk_ids=["a"]),
        EvalCase(id="c2", question="q", category="comparison", relevant_chunk_ids=["b"]),
    ]
    runs = [
        RetrievalRunCase(
            case_id="c1",
            provider="mock",
            retrieved_chunks=[RetrievedChunk(chunk_id="a", rank=1)],
        ),
        RetrievalRunCase(
            case_id="c2",
            provider="mock",
            retrieved_chunks=[RetrievedChunk(chunk_id="x", rank=1)],
        ),
    ]

    report = build_report(cases, runs, k=1)

    assert len(report.case_results) == 2
    assert len(report.summary) == 2
    markdown = render_markdown_report(report)
    assert "Benchmark Summary" in markdown
    assert "Precision@K" in markdown
