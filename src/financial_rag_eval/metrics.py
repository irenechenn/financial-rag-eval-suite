from __future__ import annotations

from collections.abc import Iterable

from financial_rag_eval.schemas import EvalCase, RetrievedChunk


def _contains_all_terms(text: str, terms: Iterable[str]) -> bool:
    lowered = text.lower()
    return all(term.lower() in lowered for term in terms)


def is_relevant(chunk: RetrievedChunk, case: EvalCase) -> bool:
    """Return whether a retrieved chunk is relevant for an eval case.

    Prefer explicit chunk-id labels. If they are unavailable, use the case's
    metadata/term criteria as a weak but inspectable relevance label.
    """

    if case.relevant_chunk_ids:
        return chunk.chunk_id in set(case.relevant_chunk_ids)

    criteria = case.relevance_criteria
    if criteria.tickers and chunk.ticker not in criteria.tickers:
        return False
    if criteria.years and chunk.year not in criteria.years:
        return False
    if criteria.required_terms and not _contains_all_terms(chunk.text, criteria.required_terms):
        return False
    return bool(criteria.tickers or criteria.years or criteria.required_terms)


def precision_at_k(retrieved: list[RetrievedChunk], case: EvalCase, k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    top_k = sorted(retrieved, key=lambda chunk: chunk.rank)[:k]
    if not top_k:
        return 0.0
    relevant = sum(1 for chunk in top_k if is_relevant(chunk, case))
    return relevant / k


def recall_at_k(retrieved: list[RetrievedChunk], case: EvalCase, k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    total_relevant = total_relevant_count(case)
    if total_relevant == 0:
        return 0.0
    top_k = sorted(retrieved, key=lambda chunk: chunk.rank)[:k]
    relevant = sum(1 for chunk in top_k if is_relevant(chunk, case))
    return min(relevant, total_relevant) / total_relevant


def relevant_retrieved_at_k(retrieved: list[RetrievedChunk], case: EvalCase, k: int) -> int:
    top_k = sorted(retrieved, key=lambda chunk: chunk.rank)[:k]
    relevant = sum(1 for chunk in top_k if is_relevant(chunk, case))
    total_relevant = total_relevant_count(case)
    return min(relevant, total_relevant) if total_relevant else 0


def total_relevant_count(case: EvalCase) -> int:
    if case.relevant_chunk_ids:
        return len(set(case.relevant_chunk_ids))
    # Weak-label mode treats the case as having one known relevant evidence target.
    return 1 if (
        case.relevance_criteria.tickers
        or case.relevance_criteria.years
        or case.relevance_criteria.required_terms
    ) else 0
