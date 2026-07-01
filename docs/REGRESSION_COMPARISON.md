# Regression Comparison

Evaluation systems should compare runs, not only score individual runs.

This project supports comparing a baseline report against a candidate report. The comparison output shows aggregate metric deltas and case-level changes.

## Command

```powershell
financial-rag-eval compare-runs `
  --baseline reports/project1_voyage_faiss_top3_unfiltered.json `
  --candidate reports/project1_voyage_faiss_top3_tool_filtered.json `
  --baseline-name unfiltered `
  --candidate-name filtered `
  --out-json reports/unfiltered_vs_filtered.json `
  --out-md reports/unfiltered_vs_filtered.md
```

## Output

| Section | Purpose |
|---|---|
| Summary Deltas | Average metric changes by case category |
| Case-Level Changes | Cases that improved or regressed |
| Newly Covered Targets | Evidence targets covered by the candidate but not the baseline |
| Newly Missed Targets | Evidence targets missed by the candidate but not the baseline |

Positive deltas mean the candidate improved over the baseline.

## Why This Matters

A retrieval system often changes over time: chunking, top-k, filters, embeddings, model providers, and query rewriting can all change results. Regression comparison makes these changes measurable and reviewable.