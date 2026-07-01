from __future__ import annotations

from collections.abc import Iterable

from financial_rag_eval.schemas import EvalCase, RelevanceCriteria, RetrievedChunk


def _contains_all_terms(text: str, terms: Iterable[str]) -> bool:
    lowered = text.lower()
    return all(term.lower() in lowered for term in terms)


def _matches_criteria(chunk: RetrievedChunk, criteria: RelevanceCriteria) -> bool:
    if criteria.tickers and chunk.ticker not in criteria.tickers:
        return False
    if criteria.years and chunk.year not in criteria.years:
        return False
    if criteria.required_terms and not _contains_all_terms(chunk.text, criteria.required_terms):
        return False
    return bool(criteria.tickers or criteria.years or criteria.required_terms)


def _target_label(target: RelevanceCriteria, index: int) -> str:
    label = getattr(target, "label", "")
    if label:
        return label
    parts = []
    if target.tickers:
        parts.append("/".join(target.tickers))
    if target.years:
        parts.append("/".join(str(year) for year in target.years))
    if target.required_terms:
        parts.append("+".join(target.required_terms))
    return " ".join(parts) if parts else f"target_{index}"


def _targets_for_case(case: EvalCase) -> list[RelevanceCriteria]:
    if case.relevance_targets:
        return list(case.relevance_targets)
    if (
        case.relevance_criteria.tickers
        or case.relevance_criteria.years
        or case.relevance_criteria.required_terms
    ):
        return [case.relevance_criteria]
    return []


def is_relevant(chunk: RetrievedChunk, case: EvalCase) -> bool:
    """Return whether a retrieved chunk is relevant for an eval case.

    Prefer explicit chunk-id labels. If they are unavailable, use target-level
    metadata/term labels. This supports multi-hop cases where recall should
    measure evidence target coverage, not just any single relevant-looking chunk.
    """

    if case.relevant_chunk_ids:
        return chunk.chunk_id in set(case.relevant_chunk_ids)

    return any(_matches_criteria(chunk, target) for target in _targets_for_case(case))


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
    return relevant_retrieved_at_k(retrieved, case, k) / total_relevant


def relevant_retrieved_at_k(retrieved: list[RetrievedChunk], case: EvalCase, k: int) -> int:
    return len(covered_target_labels(retrieved, case, k))


def covered_target_labels(retrieved: list[RetrievedChunk], case: EvalCase, k: int) -> list[str]:
    top_k = sorted(retrieved, key=lambda chunk: chunk.rank)[:k]

    if case.relevant_chunk_ids:
        retrieved_ids = {chunk.chunk_id for chunk in top_k}
        return sorted(set(case.relevant_chunk_ids) & retrieved_ids)

    covered: list[str] = []
    for index, target in enumerate(_targets_for_case(case), start=1):
        if any(_matches_criteria(chunk, target) for chunk in top_k):
            covered.append(_target_label(target, index))
    return covered


def missed_target_labels(retrieved: list[RetrievedChunk], case: EvalCase, k: int) -> list[str]:
    if case.relevant_chunk_ids:
        covered = set(covered_target_labels(retrieved, case, k))
        return sorted(set(case.relevant_chunk_ids) - covered)

    covered = set(covered_target_labels(retrieved, case, k))
    missed: list[str] = []
    for index, target in enumerate(_targets_for_case(case), start=1):
        label = _target_label(target, index)
        if label not in covered:
            missed.append(label)
    return missed


def total_relevant_count(case: EvalCase) -> int:
    if case.relevant_chunk_ids:
        return len(set(case.relevant_chunk_ids))
    return len(_targets_for_case(case))