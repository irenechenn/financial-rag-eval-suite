from financial_rag_eval.qrels_judge import judge_qrels_with_rubric, render_judge_decisions_markdown
from financial_rag_eval.schemas import EvalCase, QrelJudgment, RetrievedChunk, RetrievalRunCase


def test_rubric_judge_accepts_direct_target_evidence() -> None:
    case = EvalCase.model_validate(
        {
            "id": "case_1",
            "question": "Find Apple services revenue.",
            "category": "simple",
            "relevance_targets": [
                {
                    "label": "AAPL services revenue",
                    "tickers": ["AAPL"],
                    "years": [2024],
                    "required_terms": ["services", "revenue"],
                }
            ],
        }
    )
    run = RetrievalRunCase(
        case_id="case_1",
        retrieved_chunks=[
            RetrievedChunk(
                chunk_id="chunk_a",
                rank=1,
                ticker="AAPL",
                year=2024,
                text="Services revenue reached a record during the quarter.",
            )
        ],
    )
    qrel = QrelJudgment(
        case_id="case_1",
        chunk_id="chunk_a",
        status="candidate",
        relevance=1,
        matched_targets=["AAPL services revenue"],
    )

    decisions = judge_qrels_with_rubric([case], [run], [qrel], statuses={"candidate"})

    assert decisions[0].decision == "accepted"
    assert decisions[0].judge_model == "local-rubric-judge-v1"
    assert decisions[0].rubric_version == "retrieval-relevance-rubric-v1"


def test_rubric_judge_rejects_boilerplate() -> None:
    case = EvalCase.model_validate(
        {
            "id": "case_1",
            "question": "Find Microsoft cloud commentary.",
            "category": "simple",
            "relevance_targets": [
                {
                    "label": "MSFT cloud",
                    "tickers": ["MSFT"],
                    "years": [2024],
                    "required_terms": ["cloud"],
                }
            ],
        }
    )
    run = RetrievalRunCase(
        case_id="case_1",
        retrieved_chunks=[
            RetrievedChunk(
                chunk_id="chunk_a",
                rank=1,
                ticker="MSFT",
                year=2024,
                text="Operator Instructions. This conference call is being recorded.",
            )
        ],
    )
    qrel = QrelJudgment(
        case_id="case_1",
        chunk_id="chunk_a",
        status="candidate",
        relevance=1,
        matched_targets=["MSFT cloud"],
    )

    decisions = judge_qrels_with_rubric([case], [run], [qrel], statuses={"candidate"})
    markdown = render_judge_decisions_markdown(decisions)

    assert decisions[0].decision == "rejected"
    assert "call-opening" in decisions[0].rationale
    assert "Qrels Judge Decisions" in markdown
