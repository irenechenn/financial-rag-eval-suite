# Metrics

This project separates deterministic retrieval metrics from agent trace metrics.

## Retrieval Metrics

| Metric | Purpose | Interpretation |
|---|---|---|
| Precision@K | Measures how many of the top-k chunks are relevant | Higher means the retriever returns cleaner context |
| Recall@K | Measures how many expected evidence targets are covered | Higher means the retriever finds more required evidence |
| Hit@K | Measures whether at least one expected evidence target is found | Useful as a simple retrieval success rate |
| MRR@K | Measures how early the first relevant result appears | Higher means relevant evidence appears earlier in the ranking |

## Target-Level Recall

Simple retrieval cases usually have one expected evidence target. Multi-hop and comparison cases can have multiple targets.

Example:

```text
Question: Compare Microsoft cloud commentary with Amazon AWS commentary in 2023.
Target 1: MSFT 2023 cloud
Target 2: AMZN 2023 AWS
```

If the top-k results cover only the Microsoft target, Recall@K is `1 / 2 = 0.5`.

## Agent Trace Metrics

Agent trace metrics evaluate tool orchestration rather than retrieval ranking.

| Metric | Purpose |
|---|---|
| Tool call recall | Required tools appeared in the trace |
| Argument accuracy | Required tool arguments matched expected ticker/year/query terms |
| Tool sequence pass | Required tools appeared in the expected order |

These metrics are deterministic and do not require an LLM judge.