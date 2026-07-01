from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from financial_rag_eval.datasets import load_cases, load_retrieval_run
from financial_rag_eval.labeling import build_label_candidates
from financial_rag_eval.schemas import QrelJudgment


def build_candidate_qrels(
    cases_path: str | Path,
    run_path: str | Path,
    k: int,
    source: str,
) -> list[QrelJudgment]:
    candidates = build_label_candidates(load_cases(cases_path), load_retrieval_run(run_path), k)
    judgments: list[QrelJudgment] = []

    for case_candidates in candidates:
        for candidate in case_candidates.candidates:
            judgments.append(
                QrelJudgment(
                    case_id=case_candidates.case_id,
                    chunk_id=candidate.chunk_id,
                    relevance=1,
                    status="candidate",
                    source=source,
                    matched_targets=candidate.matched_targets,
                    notes="Generated from target-level match; requires human review.",
                )
            )

    return sorted(judgments, key=lambda item: (item.case_id, item.chunk_id))


def write_qrels_jsonl(qrels: list[QrelJudgment], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as file:
        for judgment in qrels:
            file.write(json.dumps(judgment.model_dump(), ensure_ascii=False, sort_keys=True) + "\n")


def write_qrels_markdown(qrels: list[QrelJudgment], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_qrels_markdown(qrels), encoding="utf-8")


def render_qrels_markdown(qrels: list[QrelJudgment]) -> str:
    grouped: dict[str, list[QrelJudgment]] = defaultdict(list)
    for judgment in qrels:
        grouped[judgment.case_id].append(judgment)

    status_counts: dict[str, int] = defaultdict(int)
    for judgment in qrels:
        status_counts[judgment.status] += 1

    lines = [
        "# Pooled Relevance Judgments",
        "",
        "This file summarizes pooled relevance judgments. Judgments with `candidate` status require human review before they should be treated as gold labels.",
        "",
        "## Summary",
        "",
        "| Cases With Judgments | Total Judgments | Candidate | Accepted | Rejected |",
        "|---:|---:|---:|---:|---:|",
        (
            f"| {len(grouped)} | {len(qrels)} | {status_counts['candidate']} | "
            f"{status_counts['accepted']} | {status_counts['rejected']} |"
        ),
        "",
        "## Judgments",
        "",
        "| Case | Chunk ID | Relevance | Status | Matched Targets | Source |",
        "|---|---|---:|---|---|---|",
    ]

    for judgment in qrels:
        lines.append(
            f"| {judgment.case_id} | `{judgment.chunk_id}` | {judgment.relevance} | "
            f"{judgment.status} | {'; '.join(judgment.matched_targets)} | {judgment.source} |"
        )

    lines.append("")
    return "\n".join(lines)


def export_candidate_qrels(
    cases_path: str | Path,
    run_path: str | Path,
    out_jsonl: str | Path,
    out_md: str | Path,
    k: int,
    source: str,
) -> list[QrelJudgment]:
    qrels = build_candidate_qrels(cases_path=cases_path, run_path=run_path, k=k, source=source)
    write_qrels_jsonl(qrels, out_jsonl)
    write_qrels_markdown(qrels, out_md)
    return qrels
