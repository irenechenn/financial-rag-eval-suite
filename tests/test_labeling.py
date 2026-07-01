from financial_rag_eval.labeling import build_label_candidates, render_label_candidates_markdown
from financial_rag_eval.schemas import EvalCase, RetrievedChunk, RetrievalRunCase


def test_build_label_candidates_lists_matching_chunks_and_uncovered_targets() -> None:
    case = EvalCase.model_validate(
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
    run = RetrievalRunCase(
        case_id="compare_case",
        provider="mock",
        retrieved_chunks=[
            RetrievedChunk(
                chunk_id="msft_chunk",
                rank=1,
                ticker="MSFT",
                year=2023,
                text="cloud revenue grew",
            ),
            RetrievedChunk(
                chunk_id="wrong_chunk",
                rank=2,
                ticker="GOOGL",
                year=2023,
                text="advertising revenue",
            ),
        ],
    )

    candidates = build_label_candidates([case], [run], k=2)

    assert len(candidates) == 1
    assert candidates[0].candidates[0].chunk_id == "msft_chunk"
    assert candidates[0].candidates[0].matched_targets == ["MSFT 2023 cloud"]
    assert candidates[0].uncovered_targets == ["AMZN 2023 AWS"]

    markdown = render_label_candidates_markdown(candidates)
    assert "candidate `relevant_chunk_ids`" in markdown
    assert "AMZN 2023 AWS" in markdown