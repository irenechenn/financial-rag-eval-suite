# Financial RAG Eval Suite

Companion evaluation repo for [`financial-rag-engine`](https://github.com/irenechenn/financial-rag-engine).

Project 1 built the agentic financial RAG system. This repo measures retrieval quality more formally with labeled cases, Precision@K, Recall@K, and JSON/Markdown benchmark reports.

## What This Evaluates

This project evaluates whether Project 1's FAISS + Voyage retrieval layer returns evidence with the expected company/year/topic metadata.

It intentionally keeps the MVP small:

- 24 labeled retrieval cases
- Precision@K and Recall@K
- JSON report output
- Markdown report output
- benchmark tables for GitHub/interview review

It does not include a dashboard, nDCG, production monitoring, or a large-scale benchmark suite.

## Dataset

Evaluation cases live in [`eval_cases/retrieval_v1.jsonl`](eval_cases/retrieval_v1.jsonl).

Current v1 categories:

| Category | Cases | Purpose |
|---|---:|---|
| simple | 10 | Single-company, single-year retrieval |
| metadata_filtered | 6 | Ticker/year-specific retrieval checks |
| multi_hop | 4 | Cross-year retrieval questions |
| comparison | 4 | Cross-company comparison retrieval questions |

The v1 labels use inspectable relevance targets: expected ticker, expected year, and required terms. Simple cases usually have one target; multi-hop and comparison cases can require multiple targets, such as `MSFT 2023 cloud` plus `AMZN 2023 AWS`. The metric code also supports explicit `relevant_chunk_ids`, which should be the next dataset-hardening step.

## Metrics

Precision@K answers: among the top K retrieved chunks, how many were relevant?

```text
Precision@K = relevant retrieved chunks in top K / K
```

Recall@K answers: among the known relevant evidence targets, how many were covered in the top K?

```text
Recall@K = covered evidence targets in top K / total evidence targets
```

For multi-hop and comparison cases, Recall@K measures target coverage. For example, a question comparing Microsoft cloud and Amazon AWS has two targets; retrieving only Microsoft evidence gives partial recall even if the retrieved chunks are relevant.

## Benchmark Results

Real Project 1 retrieval run, `top_k=3`, Voyage finance embeddings, FAISS `IndexFlatIP` over L2-normalized vectors.

### Unfiltered Semantic Retrieval

This run searches with the question text only. It measures how well semantic retrieval finds the right evidence without applying expected ticker/year filters.

| Provider | Case Type | Cases | Precision@3 | Recall@3 | Runtime Errors |
|---|---|---:|---:|---:|---:|
| voyage-faiss | comparison | 4 | 0.417 | 0.500 | 0 |
| voyage-faiss | metadata_filtered | 6 | 0.389 | 0.667 | 0 |
| voyage-faiss | multi_hop | 4 | 0.583 | 0.750 | 0 |
| voyage-faiss | simple | 10 | 0.333 | 0.700 | 0 |

### Tool-Style Filtered Retrieval

This run applies expected ticker/year filters when the case has a single expected ticker and year, matching the way Project 1's search tool is often used by the agent.

| Provider | Case Type | Cases | Precision@3 | Recall@3 | Runtime Errors |
|---|---|---:|---:|---:|---:|
| voyage-faiss-filtered | comparison | 4 | 0.833 | 0.625 | 0 |
| voyage-faiss-filtered | metadata_filtered | 6 | 0.556 | 0.833 | 0 |
| voyage-faiss-filtered | multi_hop | 4 | 0.583 | 0.750 | 0 |
| voyage-faiss-filtered | simple | 10 | 0.733 | 1.000 | 0 |

## Interpretation

The filtered run scores higher because metadata constraints remove wrong-company and wrong-year chunks before ranking. That is expected and useful: Project 1's agent is designed to call retrieval with ticker/year arguments when it can infer them. The target-level recall scores also show a useful limitation: comparison questions may retrieve strong evidence for one side while missing the second required evidence target.

The unfiltered run is still useful as a harder semantic retrieval baseline. It shows where the query alone is not enough and where metadata-aware tool calls matter.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

## Validate Cases

```powershell
financial-rag-eval validate-cases eval_cases/retrieval_v1.jsonl
```

## Run Project 1 Retrieval

Requires Project 1's `.env` with `VOYAGE_API_KEY` and an existing Project 1 FAISS index.

```powershell
financial-rag-eval run-project1-retrieval `
  --cases eval_cases/retrieval_v1.jsonl `
  --out sample_runs/project1_voyage_faiss_top3_unfiltered.jsonl `
  --top-k 3
```

Filtered/tool-style run:

```powershell
financial-rag-eval run-project1-retrieval `
  --cases eval_cases/retrieval_v1.jsonl `
  --out sample_runs/project1_voyage_faiss_top3_tool_filtered.jsonl `
  --top-k 3 `
  --provider voyage-faiss-filtered `
  --use-expected-filters
```

## Score A Retrieval Run

```powershell
financial-rag-eval score-run `
  --cases eval_cases/retrieval_v1.jsonl `
  --run sample_runs/project1_voyage_faiss_top3_unfiltered.jsonl `
  --k 3 `
  --out-json reports/project1_voyage_faiss_top3_unfiltered.json `
  --out-md reports/project1_voyage_faiss_top3_unfiltered.md
```

## Tests

```powershell
pytest
```

Current status: `6 passed`.

## Limitations

- The v1 dataset is small and interview-defensible, not production-grade.
- Weak labels are useful for quick evaluation, but explicit stable `relevant_chunk_ids` would make the benchmark stricter.
- Precision/Recall here evaluate retrieval, not final answer correctness.
- The filtered benchmark uses expected metadata when available, so it should be interpreted as tool-style retrieval rather than pure semantic search.

## Resume Bullet

Built a companion RAG evaluation suite for a financial transcript QA agent, expanding the benchmark to 24 labeled retrieval cases and adding Precision@K/Recall@K metrics with JSON and Markdown benchmark reports.