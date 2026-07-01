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
    assert "Failure Analysis" in markdown
    assert "c2" in markdown
    assert "b" in markdown


def test_report_includes_target_level_misses() -> None:
    cases = [
        EvalCase.model_validate(
            {
                "id": "compare_case",
                "question": "q",
                "category": "comparison",
                "relevance_targets": [
                    {
                        "label": "MSFT 2023 cloud",
                        "tickers": ["MSFT"],
                        "years": [2023],
                        "required_terms": ["cloud"],
                    },
                    {
                        "label": "AMZN 2023 AWS",
                        "tickers": ["AMZN"],
                        "years": [2023],
                        "required_terms": ["aws"],
                    },
                ],
            }
        )
    ]
    runs = [
        RetrievalRunCase(
            case_id="compare_case",
            provider="mock",
            retrieved_chunks=[
                RetrievedChunk(
                    chunk_id="x",
                    rank=1,
                    ticker="MSFT",
                    year=2023,
                    text="cloud revenue",
                )
            ],
        )
    ]

    report = build_report(cases, runs, k=1)
    result = report.case_results[0]
    assert result.covered_targets == ["MSFT 2023 cloud"]
    assert result.missed_targets == ["AMZN 2023 AWS"]

    markdown = render_markdown_report(report)
    assert "MSFT 2023 cloud" in markdown
    assert "AMZN 2023 AWS" in markdown