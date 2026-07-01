# Label Hardening

The initial benchmark uses target-level labels: ticker, year, and required topic terms. This is inspectable and useful, but stricter retrieval benchmarks usually use stable relevance judgments such as explicit `relevant_chunk_ids`.

This project includes a label candidate audit command to support that process without silently converting model output into gold labels.

## Command

```powershell
financial-rag-eval suggest-labels `
  --cases eval_cases/retrieval_v1.jsonl `
  --run sample_runs/project1_voyage_faiss_top3_tool_filtered.jsonl `
  --k 3 `
  --out-jsonl label_candidates/tool_filtered_top3.jsonl `
  --out-md label_candidates/tool_filtered_top3.md
```

## Output

The audit report lists retrieved chunk IDs that matched existing target-level labels, along with matched targets and text previews.

These are candidate labels for human review. They should not be treated as final gold labels until reviewed.

## Why This Matters

Explicit chunk-id labels make Precision@K, Recall@K, Hit@K, and MRR@K stricter because the benchmark no longer relies only on metadata and term matching.

## Recommended Workflow

1. Run retrieval against the labeled cases.
2. Generate label candidates.
3. Review candidate chunks manually.
4. Promote confirmed chunk IDs into `relevant_chunk_ids`.
5. Re-run benchmark reports.