# Agent Trace Evaluation

Project 1 uses a ReAct-style agent that can call tools before producing a final answer. Retrieval metrics alone do not evaluate whether the agent used the tools correctly.

This project includes deterministic agent trace metrics for tool orchestration.

## Trace Inputs

An agent trace evaluation case defines required tool calls:

```json
{
  "case_id": "msft_cloud_vs_amzn_aws_2023",
  "required_tool_calls": [
    {"tool_name": "search_transcript_tool", "ticker": "MSFT", "year": 2023, "query_terms": ["cloud"]},
    {"tool_name": "search_transcript_tool", "ticker": "AMZN", "year": 2023, "query_terms": ["aws"]}
  ]
}
```

A trace run provides observed tool calls with arguments and step order.

## Metrics

| Metric | Meaning |
|---|---|
| Tool call recall | Fraction of required tool calls that appeared |
| Argument accuracy | Fraction of required tool calls with matching arguments |
| Tool sequence pass | Whether required tools appeared in the expected order |

## Why This Matters

For agentic RAG, final answer quality can hide orchestration failures. Trace-level metrics expose whether the agent searched the right company, year, and topic before answering.