# Judge Agreement Report

This report compares relevance decisions from two qrels judges over the same pooled judgments.

## Summary

| Baseline | Candidate | Shared Decisions | Agreements | Disagreements | Agreement Rate |
|---|---|---:|---:|---:|---:|
| local_rubric_judge_v1 | claude_judge | 49 | 46 | 3 | 0.939 |

## Disagreements

| Case | Chunk ID | Baseline | Candidate | Baseline Rationale | Candidate Rationale |
|---|---|---|---|---|---|
| aapl_2023_services_revenue | `AAPL_2023_Q4.0_r15_c18` | accepted | rejected | Preview contains the required target terms and is not call-opening boilerplate. | This chunk is an analyst's question referencing Services revenue in passing, not a substantive comment or data point on Apple's 2023 services revenue itself. |
| amzn_2024_aws_metadata | `AMZN_2024_Q4.0_r40_c8` | rejected | accepted | Preview appears to be call-opening or logistics text rather than evidence. | The chunk directly discusses AWS operating margins for Amazon, matching the AMZN 2024 AWS target. |
| msft_2024_cloud | `MSFT_2024_Q3.0_r100_c12` | rejected | accepted | Preview does not directly support the matched target; missing cloud. | The chunk discusses scaling cloud/AI infrastructure spend based on demand signals, which directly relates to Microsoft's 2024 cloud commentary on capacity and growth strategy. |

## Coverage

| Check | Values |
|---|---|
| Baseline-only decisions | _None_ |
| Candidate-only decisions | _None_ |
