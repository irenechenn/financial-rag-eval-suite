from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from financial_rag_eval.datasets import load_cases, load_retrieval_run
from financial_rag_eval.metrics import matching_target_labels
from financial_rag_eval.schemas import EvalCase, RelevanceCriteria, RetrievalRunCase


class ChunkLabelCandidate(BaseModel):
    chunk_id: str
    rank: int
    score: float | None = None
    ticker: str | None = None
    year: int | None = None
    quarter: str | None = None
    matched_targets: list[str] = Field(default_factory=list)
    text_preview: str = ""


class CaseLabelCandidates(BaseModel):
    case_id: str
    category: str
    provider: str
    candidates: list[ChunkLabelCandidate] = Field(default_factory=list)
    uncovered_targets: list[str] = Field(default_factory=list)


def build_label_candidates(
    cases: list[EvalCase],
    runs: list[RetrievalRunCase],
    k: int,
) -> list[CaseLabelCandidates]:
    cases_by_id = {case.id: case for case in cases}
    output: list[CaseLabelCandidates] = []

    for run in runs:
        case = cases_by_id.get(run.case_id)
        if case is None:
            raise ValueError(f"Run references unknown case_id: {run.case_id}")

        candidates: list[ChunkLabelCandidate] = []
        covered_targets: set[str] = set()
        for chunk in sorted(run.retrieved_chunks, key=lambda item: item.rank)[:k]:
            matched_targets = matching_target_labels(chunk, case)
            if not matched_targets:
                continue
            covered_targets.update(matched_targets)
            candidates.append(
                ChunkLabelCandidate(
                    chunk_id=chunk.chunk_id,
                    rank=chunk.rank,
                    score=chunk.score,
                    ticker=chunk.ticker,
                    year=chunk.year,
                    quarter=chunk.quarter,
                    matched_targets=matched_targets,
                    text_preview=_preview_text(chunk.text),
                )
            )

        expected_targets = _expected_target_labels(case)
        output.append(
            CaseLabelCandidates(
                case_id=case.id,
                category=case.category,
                provider=run.provider,
                candidates=candidates,
                uncovered_targets=[target for target in expected_targets if target not in covered_targets],
            )
        )

    return output


def write_label_candidates_jsonl(candidates: list[CaseLabelCandidates], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as file:
        for item in candidates:
            file.write(json.dumps(item.model_dump(), ensure_ascii=False) + "\n")


def write_label_candidates_markdown(candidates: list[CaseLabelCandidates], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_label_candidates_markdown(candidates), encoding="utf-8")


def render_label_candidates_markdown(candidates: list[CaseLabelCandidates]) -> str:
    lines = [
        "# Relevance Label Candidate Audit",
        "",
        "This report lists retrieved chunks that matched target-level labels. These are candidate `relevant_chunk_ids` for human review, not automatically accepted gold labels.",
        "",
        "## Summary",
        "",
        "| Cases | Cases With Candidates | Cases With Uncovered Targets | Candidate Chunk IDs |",
        "|---:|---:|---:|---:|",
    ]
    cases_with_candidates = sum(1 for item in candidates if item.candidates)
    cases_with_uncovered = sum(1 for item in candidates if item.uncovered_targets)
    candidate_ids = sum(len(item.candidates) for item in candidates)
    lines.append(
        f"| {len(candidates)} | {cases_with_candidates} | {cases_with_uncovered} | {candidate_ids} |"
    )

    lines.extend([
        "",
        "## Candidate Labels",
        "",
        "| Case | Category | Chunk ID | Rank | Matched Targets | Preview |",
        "|---|---|---|---:|---|---|",
    ])
    for item in candidates:
        for candidate in item.candidates:
            matched_targets = "; ".join(_escape_markdown_cell(target) for target in candidate.matched_targets)
            lines.append(
                f"| {item.case_id} | {item.category} | `{candidate.chunk_id}` | {candidate.rank} | "
                f"{matched_targets} | {_escape_markdown_cell(candidate.text_preview)} |"
            )

    lines.extend([
        "",
        "## Uncovered Targets",
        "",
        "| Case | Category | Uncovered Targets |",
        "|---|---|---|",
    ])
    for item in candidates:
        if item.uncovered_targets:
            lines.append(
                f"| {item.case_id} | {item.category} | "
                f"{'; '.join(_escape_markdown_cell(target) for target in item.uncovered_targets)} |"
            )

    lines.append("")
    return "\n".join(lines)


def generate_label_candidates(
    cases_path: str | Path,
    run_path: str | Path,
    out_jsonl: str | Path,
    out_md: str | Path,
    k: int,
) -> list[CaseLabelCandidates]:
    candidates = build_label_candidates(load_cases(cases_path), load_retrieval_run(run_path), k)
    write_label_candidates_jsonl(candidates, out_jsonl)
    write_label_candidates_markdown(candidates, out_md)
    return candidates


def _expected_target_labels(case: EvalCase) -> list[str]:
    if case.relevant_chunk_ids:
        return list(case.relevant_chunk_ids)
    if case.relevance_targets:
        return [_criteria_label(target, index) for index, target in enumerate(case.relevance_targets, start=1)]
    if case.relevance_criteria.tickers or case.relevance_criteria.years or case.relevance_criteria.required_terms:
        return [_criteria_label(case.relevance_criteria, 1)]
    return []


def _criteria_label(criteria: RelevanceCriteria, index: int) -> str:
    if criteria.label:
        return criteria.label
    parts = []
    if criteria.tickers:
        parts.append("/".join(criteria.tickers))
    if criteria.years:
        parts.append("/".join(str(year) for year in criteria.years))
    if criteria.required_terms:
        parts.append("+".join(criteria.required_terms))
    return " ".join(parts) if parts else f"target_{index}"


def _escape_markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _preview_text(text: str, limit: int = 240) -> str:
    normalized = " ".join(text.split())
    ascii_text = normalized.encode("ascii", errors="ignore").decode("ascii")
    return ascii_text[:limit]
