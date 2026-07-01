from financial_rag_eval.qrels_review import build_qrels_review_packet, render_review_packet_markdown
from financial_rag_eval.schemas import EvalCase, QrelJudgment, RetrievedChunk, RetrievalRunCase


def test_build_qrels_review_packet_includes_candidate_context() -> None:
    cases = [
        EvalCase(
            id="case_1",
            question="Find Apple services revenue commentary.",
            category="simple",
        )
    ]
    runs = [
        RetrievalRunCase(
            case_id="case_1",
            provider="mock",
            retrieved_chunks=[
                RetrievedChunk(
                    chunk_id="chunk_a",
                    rank=2,
                    ticker="AAPL",
                    year=2024,
                    quarter="Q4",
                    text="Services revenue reached a record during the quarter.",
                )
            ],
        )
    ]
    qrels = [
        QrelJudgment(
            case_id="case_1",
            chunk_id="chunk_a",
            relevance=1,
            status="candidate",
            matched_targets=["AAPL 2024 services revenue"],
        ),
        QrelJudgment(case_id="case_1", chunk_id="chunk_b", relevance=1, status="accepted"),
    ]

    items = build_qrels_review_packet(cases, runs, qrels, statuses={"candidate"})

    assert len(items) == 1
    assert items[0].chunk_id == "chunk_a"
    assert items[0].rank == 2
    assert items[0].decision == "pending"
    assert "Services revenue" in items[0].preview

    markdown = render_review_packet_markdown(items)
    assert "Qrels Review Packet" in markdown
    assert "[ ] `accepted` / [ ] `rejected`" in markdown
    assert "Find Apple services revenue commentary." in markdown
