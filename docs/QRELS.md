# Pooled Qrels

Retrieval benchmarks usually need relevance judgments: query/document pairs marked as relevant or not relevant. In this project those judgments are stored as JSONL qrels.

The v1 workflow keeps qrels separate from eval cases so candidate labels do not silently change the benchmark definition.

## Schema

Each qrel record contains:

| Field | Meaning |
|---|---|
| `case_id` | Eval case identifier |
| `chunk_id` | Retrieved transcript chunk identifier |
| `relevance` | Integer relevance grade, currently `1` for relevant candidates |
| `status` | `candidate`, `accepted`, or `rejected` |
| `source` | Retrieval run or labeling source that produced the judgment |
| `matched_targets` | Evidence targets matched by the chunk |
| `notes` | Review notes |

## Workflow

1. Run a retrieval benchmark.
2. Export pooled candidate qrels from the top-k results.
3. Review each candidate chunk.
4. Mark reviewed judgments as `accepted` or `rejected`.
5. Promote accepted qrels into stricter gold labels or use them in a qrels-based scorer.

## Command

```powershell
financial-rag-eval export-qrels `
  --cases eval_cases/retrieval_v1.jsonl `
  --run sample_runs/project1_voyage_faiss_top3_tool_filtered.jsonl `
  --k 3 `
  --source project1_voyage_faiss_top3_tool_filtered `
  --out-jsonl qrels/retrieval_v1_pooled_top3.jsonl `
  --out-md qrels/retrieval_v1_pooled_top3.md
```

## Scoring With Qrels

By default, qrels scoring uses only `accepted` judgments:

```powershell
financial-rag-eval score-qrels `
  --cases eval_cases/retrieval_v1.jsonl `
  --run sample_runs/project1_voyage_faiss_top3_tool_filtered.jsonl `
  --qrels qrels/retrieval_v1_pooled_top3.jsonl `
  --k 3 `
  --out-json reports/project1_voyage_faiss_top3_tool_filtered_qrels.json `
  --out-md reports/project1_voyage_faiss_top3_tool_filtered_qrels.md
```

For workflow validation with unreviewed pooled candidates, include candidate judgments explicitly:

```powershell
financial-rag-eval score-qrels `
  --cases eval_cases/retrieval_v1.jsonl `
  --run sample_runs/project1_voyage_faiss_top3_tool_filtered.jsonl `
  --qrels qrels/retrieval_v1_pooled_top3.jsonl `
  --judgment-status candidate `
  --k 3 `
  --out-json reports/project1_voyage_faiss_top3_tool_filtered_qrels_candidate.json `
  --out-md reports/project1_voyage_faiss_top3_tool_filtered_qrels_candidate.md
```

## Why Separate Qrels Matter

Target-level labels are useful for early evaluation, but explicit qrels are closer to standard information retrieval practice. Keeping candidate qrels separate makes it clear which labels are generated for review and which labels have been accepted as gold.
