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
3. Review each candidate chunk with a human reviewer, rubric judge, or independent LLM judge.
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

## Auditing Qrels

Audit reports check qrel coverage and data quality before scoring:

```powershell
financial-rag-eval audit-qrels `
  --cases eval_cases/retrieval_v1.jsonl `
  --qrels qrels/retrieval_v1_pooled_top3.jsonl `
  --out-json qrels/retrieval_v1_pooled_top3_audit.json `
  --out-md qrels/retrieval_v1_pooled_top3_audit.md
```

The audit checks status counts, relevance-grade counts, source counts, category coverage, unlabeled cases, unknown case IDs, and duplicate judgments.

## Review Packet

Review packets turn candidate qrels into a checklist with the original question, chunk metadata, matched targets, and text preview:

```powershell
financial-rag-eval make-review-packet `
  --cases eval_cases/retrieval_v1.jsonl `
  --run sample_runs/project1_voyage_faiss_top3_tool_filtered.jsonl `
  --qrels qrels/retrieval_v1_pooled_top3.jsonl `
  --judgment-status candidate `
  --out-jsonl qrels/retrieval_v1_review_packet.jsonl `
  --out-md qrels/retrieval_v1_review_packet.md
```

This packet is meant for review by a human, rubric judge, or independent LLM judge. Updating qrel statuses to `accepted` or `rejected` should happen only after inspecting whether the chunk directly supports the matched target.

## Judge Review

The local rubric judge is a deterministic baseline for the review loop:

```powershell
financial-rag-eval judge-qrels `
  --cases eval_cases/retrieval_v1.jsonl `
  --run sample_runs/project1_voyage_faiss_top3_tool_filtered.jsonl `
  --qrels qrels/retrieval_v1_pooled_top3.jsonl `
  --judgment-status candidate `
  --out-jsonl qrels/retrieval_v1_rubric_judge_decisions.jsonl `
  --out-md qrels/retrieval_v1_rubric_judge_decisions.md
```

Each judge decision records `decision`, `confidence`, `rationale`, `judge_model`, and `rubric_version`. The same schema can be used by a stronger independent LLM judge.

Claude judge example:

```powershell
financial-rag-eval judge-qrels `
  --cases eval_cases/retrieval_v1.jsonl `
  --run sample_runs/project1_voyage_faiss_top3_tool_filtered.jsonl `
  --qrels qrels/retrieval_v1_pooled_top3.jsonl `
  --judge-provider claude `
  --judgment-status candidate `
  --out-jsonl qrels/retrieval_v1_claude_judge_decisions.jsonl `
  --out-md qrels/retrieval_v1_claude_judge_decisions.md
```

Judge agreement reports compare decision consistency across judges:

```powershell
financial-rag-eval compare-judges `
  --baseline qrels/retrieval_v1_rubric_judge_decisions.jsonl `
  --candidate qrels/retrieval_v1_claude_judge_decisions.jsonl `
  --baseline-name local_rubric_judge_v1 `
  --candidate-name claude_judge `
  --out-json qrels/rubric_vs_claude_judge_agreement.json `
  --out-md qrels/rubric_vs_claude_judge_agreement.md
```

## Applying Review Decisions

Review decisions can be applied to pooled qrels to produce a mixed accepted/rejected/candidate qrels file:

```powershell
financial-rag-eval apply-review-decisions `
  --qrels qrels/retrieval_v1_pooled_top3.jsonl `
  --decisions qrels/retrieval_v1_assisted_review.jsonl `
  --source assisted_review `
  --out-jsonl qrels/retrieval_v1_assisted_reviewed_qrels.jsonl `
  --out-md qrels/retrieval_v1_assisted_reviewed_qrels.md
```

The included assisted review seed is useful for exercising the full qrels workflow. It should be treated as model-assisted labeling, not production benchmark labels.

## Why Separate Qrels Matter

Target-level labels are useful for early evaluation, but explicit qrels are closer to standard information retrieval practice. Keeping candidate qrels separate makes it clear which labels are generated for review and which labels have been accepted as gold.
