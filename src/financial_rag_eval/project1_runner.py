from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from financial_rag_eval.datasets import load_cases
from financial_rag_eval.schemas import EvalCase, RetrievedChunk, RetrievalRunCase


def _project1_chunk_id(metadata: dict[str, Any]) -> str:
    ticker = metadata.get("ticker", "UNK")
    year = metadata.get("year", "UNK")
    quarter = metadata.get("quarter", "UNK")
    record_index = metadata.get("record_index", "UNK")
    chunk_index = metadata.get("chunk_index", "UNK")
    return f"{ticker}_{year}_Q{quarter}_r{record_index}_c{chunk_index}"


def _single_or_none(values: list[Any]) -> Any | None:
    return values[0] if len(values) == 1 else None


async def run_project1_retrieval(
    cases_path: str | Path,
    output_path: str | Path,
    project1_path: str | Path,
    index_path: str | Path,
    top_k: int,
    provider: str = "voyage-faiss",
    use_expected_filters: bool = False,
) -> list[RetrievalRunCase]:
    """Run Project 1 FAISS retrieval for Project 2 eval cases.

    By default this evaluates unfiltered semantic retrieval. Passing
    use_expected_filters=True evaluates the Project 1 tool-style path when a
    case has exactly one expected ticker and one expected year.
    """

    project1_root = Path(project1_path).resolve()
    sys.path.insert(0, str(project1_root))

    from src.providers.voyage_prov import VoyageEmbeddingProvider  # noqa: PLC0415
    from src.vector_store import FaissVectorStore  # noqa: PLC0415

    cases = load_cases(cases_path)
    embeddings = VoyageEmbeddingProvider()
    store = FaissVectorStore.load(Path(index_path))

    runs: list[RetrievalRunCase] = []
    for case in cases:
        filters = _filters_for_case(case) if use_expected_filters else None
        try:
            results = await store.search(
                case.question,
                embeddings,
                top_k=top_k,
                filters=filters,
            )
            chunks = [
                RetrievedChunk(
                    chunk_id=_project1_chunk_id(result.metadata),
                    rank=rank,
                    score=result.score,
                    text=result.text,
                    ticker=result.metadata.get("ticker"),
                    year=result.metadata.get("year"),
                    quarter=str(result.metadata.get("quarter")),
                )
                for rank, result in enumerate(results, start=1)
            ]
            runs.append(
                RetrievalRunCase(
                    case_id=case.id,
                    provider=provider,
                    retrieved_chunks=chunks,
                )
            )
        except Exception as exc:  # noqa: BLE001
            runs.append(
                RetrievalRunCase(
                    case_id=case.id,
                    provider=provider,
                    retrieved_chunks=[],
                    runtime_error=f"{type(exc).__name__}: {exc}",
                )
            )

    _write_run_jsonl(runs, output_path)
    return runs


def _filters_for_case(case: EvalCase) -> dict[str, Any] | None:
    ticker = _single_or_none(case.expected_tickers)
    year = _single_or_none(case.expected_years)
    if ticker is None and year is None:
        return None
    return {"ticker": ticker, "year": year}


def _write_run_jsonl(runs: list[RetrievalRunCase], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for run in runs:
            file.write(json.dumps(run.model_dump(), ensure_ascii=False) + "\n")


def run_project1_retrieval_sync(
    cases_path: str | Path,
    output_path: str | Path,
    project1_path: str | Path,
    index_path: str | Path,
    top_k: int,
    provider: str = "voyage-faiss",
    use_expected_filters: bool = False,
) -> list[RetrievalRunCase]:
    return asyncio.run(
        run_project1_retrieval(
            cases_path=cases_path,
            output_path=output_path,
            project1_path=project1_path,
            index_path=index_path,
            top_k=top_k,
            provider=provider,
            use_expected_filters=use_expected_filters,
        )
    )
