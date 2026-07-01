from financial_rag_eval.metrics import hit_at_k, precision_at_k, recall_at_k, reciprocal_rank_at_k
from financial_rag_eval.schemas import EvalCase, RetrievedChunk


def test_precision_and_recall_with_explicit_chunk_ids() -> None:
    case = EvalCase(
        id="case_1",
        question="question",
        category="simple",
        relevant_chunk_ids=["a", "c"],
    )
    retrieved = [
        RetrievedChunk(chunk_id="a", rank=1),
        RetrievedChunk(chunk_id="b", rank=2),
        RetrievedChunk(chunk_id="c", rank=3),
    ]

    assert precision_at_k(retrieved, case, 2) == 0.5
    assert recall_at_k(retrieved, case, 2) == 0.5
    assert precision_at_k(retrieved, case, 3) == 2 / 3
    assert recall_at_k(retrieved, case, 3) == 1.0


def test_empty_retrieval_scores_zero() -> None:
    case = EvalCase(
        id="case_1",
        question="question",
        category="simple",
        relevant_chunk_ids=["a"],
    )

    assert precision_at_k([], case, 3) == 0.0
    assert recall_at_k([], case, 3) == 0.0


def test_weak_relevance_criteria() -> None:
    case = EvalCase.model_validate(
        {
            "id": "aapl_services",
            "question": "question",
            "category": "simple",
            "relevance_criteria": {
                "tickers": ["AAPL"],
                "years": [2023],
                "required_terms": ["services"],
            },
        }
    )
    retrieved = [
        RetrievedChunk(
            chunk_id="x",
            rank=1,
            ticker="AAPL",
            year=2023,
            text="Services revenue grew during the quarter.",
        ),
        RetrievedChunk(
            chunk_id="y",
            rank=2,
            ticker="MSFT",
            year=2023,
            text="Cloud revenue grew.",
        ),
    ]

    assert precision_at_k(retrieved, case, 2) == 0.5
    assert recall_at_k(retrieved, case, 2) == 1.0


def test_weak_recall_is_capped_at_one() -> None:
    case = EvalCase.model_validate(
        {
            "id": "msft_cloud",
            "question": "question",
            "category": "simple",
            "relevance_criteria": {
                "tickers": ["MSFT"],
                "years": [2024],
                "required_terms": ["cloud"],
            },
        }
    )
    retrieved = [
        RetrievedChunk(chunk_id="x", rank=1, ticker="MSFT", year=2024, text="cloud revenue"),
        RetrievedChunk(chunk_id="y", rank=2, ticker="MSFT", year=2024, text="cloud demand"),
    ]

    assert precision_at_k(retrieved, case, 2) == 1.0
    assert recall_at_k(retrieved, case, 2) == 1.0


def test_target_level_recall_counts_covered_targets() -> None:
    case = EvalCase.model_validate(
        {
            "id": "msft_vs_amzn",
            "question": "question",
            "category": "comparison",
            "relevance_targets": [
                {
                    "label": "MSFT cloud",
                    "tickers": ["MSFT"],
                    "years": [2023],
                    "required_terms": ["cloud"],
                },
                {
                    "label": "AMZN AWS",
                    "tickers": ["AMZN"],
                    "years": [2023],
                    "required_terms": ["aws"],
                },
            ],
        }
    )
    retrieved = [
        RetrievedChunk(chunk_id="x", rank=1, ticker="MSFT", year=2023, text="cloud revenue"),
        RetrievedChunk(chunk_id="y", rank=2, ticker="MSFT", year=2023, text="cloud demand"),
    ]

    assert precision_at_k(retrieved, case, 2) == 1.0
    assert recall_at_k(retrieved, case, 2) == 0.5

def test_hit_and_reciprocal_rank_at_k() -> None:
    case = EvalCase(
        id="case_1",
        question="question",
        category="simple",
        relevant_chunk_ids=["c"],
    )
    retrieved = [
        RetrievedChunk(chunk_id="a", rank=1),
        RetrievedChunk(chunk_id="b", rank=2),
        RetrievedChunk(chunk_id="c", rank=3),
    ]

    assert hit_at_k(retrieved, case, 2) == 0.0
    assert reciprocal_rank_at_k(retrieved, case, 2) == 0.0
    assert hit_at_k(retrieved, case, 3) == 1.0
    assert reciprocal_rank_at_k(retrieved, case, 3) == 1 / 3