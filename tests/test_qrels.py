from financial_rag_eval.qrels import render_qrels_markdown
from financial_rag_eval.schemas import QrelJudgment


def test_render_qrels_markdown_summarizes_candidate_judgments() -> None:
    qrels = [
        QrelJudgment(
            case_id="case_1",
            chunk_id="chunk_a",
            relevance=1,
            status="candidate",
            source="mock-run",
            matched_targets=["AAPL 2024 services"],
        ),
        QrelJudgment(
            case_id="case_1",
            chunk_id="chunk_b",
            relevance=1,
            status="accepted",
            source="mock-run",
            matched_targets=["AAPL 2024 services"],
        ),
    ]

    markdown = render_qrels_markdown(qrels)

    assert "Pooled Relevance Judgments" in markdown
    assert "| 1 | 2 | 1 | 1 | 0 |" in markdown
    assert "`chunk_a`" in markdown
    assert "mock-run" in markdown
