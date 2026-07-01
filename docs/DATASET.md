# Dataset Design

Evaluation cases are stored as JSONL in `eval_cases/retrieval_v1.jsonl`.

## Case Categories

| Category | Description |
|---|---|
| simple | Single-company, single-year retrieval |
| metadata_filtered | Cases that require correct ticker/year specificity |
| multi_hop | Same company across multiple years |
| comparison | Multiple companies or evidence targets |

## Labeling Policy

Each case can define one or more `relevance_targets`.

A target is an inspectable label with:

- `label`
- `tickers`
- `years`
- `required_terms`

The benchmark also supports explicit `relevant_chunk_ids`. Stable chunk-id labels are stricter and are a recommended future hardening step.

## Current Scope

The current v1 dataset has 24 labeled retrieval cases. It is a focused benchmark for regression testing and retrieval analysis, not a broad production benchmark.