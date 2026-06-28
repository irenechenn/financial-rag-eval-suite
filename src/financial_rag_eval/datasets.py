from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from financial_rag_eval.schemas import EvalCase, RetrievalRunCase

T = TypeVar("T", bound=BaseModel)


def _load_jsonl(path: Path, model: type[T]) -> list[T]:
    records: list[T] = []
    with path.open("r", encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(model.model_validate(json.loads(stripped)))
            except Exception as exc:  # noqa: BLE001
                raise ValueError(f"Invalid JSONL record at {path}:{line_number}: {exc}") from exc
    return records


def load_cases(path: str | Path) -> list[EvalCase]:
    return _load_jsonl(Path(path), EvalCase)


def load_retrieval_run(path: str | Path) -> list[RetrievalRunCase]:
    return _load_jsonl(Path(path), RetrievalRunCase)
