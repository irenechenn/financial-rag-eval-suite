# Qrels Judge Decisions

These decisions were produced by an independent qrels judge. They are useful for exercising the judge-review workflow and should be spot-checked before being treated as production benchmark labels.

## Rubric

| Version | `retrieval-relevance-rubric-v1` |
|---|---|
| Judge model | `local-rubric-judge-v1` |

## Summary

| Decisions | Accepted | Rejected |
|---:|---:|---:|
| 49 | 13 | 36 |

## Decisions

| Case | Chunk ID | Decision | Confidence | Rationale |
|---|---|---|---:|---|
| aapl_2023_services_revenue | `AAPL_2023_Q1.0_r12_c2` | rejected | 0.75 | Preview does not directly support the matched target; missing services. |
| aapl_2023_services_revenue | `AAPL_2023_Q4.0_r15_c18` | accepted | 0.85 | Preview contains the required target terms and is not call-opening boilerplate. |
| aapl_2024_services_metadata | `AAPL_2024_Q2.0_r17_c0` | rejected | 0.90 | Preview appears to be call-opening or logistics text rather than evidence. |
| aapl_2024_services_metadata | `AAPL_2024_Q4.0_r19_c0` | rejected | 0.90 | Preview appears to be call-opening or logistics text rather than evidence. |
| aapl_2024_services_metadata | `AAPL_2024_Q4.0_r19_c10` | rejected | 0.75 | Preview does not directly support the matched target; missing services. |
| aapl_services_2023_vs_2024 | `AAPL_2024_Q4.0_r19_c10` | rejected | 0.75 | Preview does not directly support the matched target; missing services. |
| aapl_services_vs_msft_cloud_2024 | `AAPL_2024_Q3.0_r18_c11` | accepted | 0.85 | Preview contains the required target terms and is not call-opening boilerplate. |
| aapl_services_vs_msft_cloud_2024 | `AAPL_2024_Q4.0_r19_c10` | rejected | 0.75 | Preview does not directly support the matched target; missing services. |
| aapl_services_vs_msft_cloud_2024 | `MSFT_2024_Q3.0_r100_c0` | rejected | 0.90 | Preview appears to be call-opening or logistics text rather than evidence. |
| amzn_2023_aws | `AMZN_2023_Q3.0_r35_c11` | rejected | 0.75 | Preview does not directly support the matched target; missing aws. |
| amzn_2023_aws | `AMZN_2023_Q4.0_r36_c14` | accepted | 0.85 | Preview contains the required target terms and is not call-opening boilerplate. |
| amzn_2023_aws | `AMZN_2023_Q4.0_r36_c15` | rejected | 0.75 | Preview does not directly support the matched target; missing aws. |
| amzn_2024_aws_metadata | `AMZN_2024_Q1.0_r37_c8` | rejected | 0.75 | Preview does not directly support the matched target; missing aws. |
| amzn_2024_aws_metadata | `AMZN_2024_Q3.0_r39_c0` | rejected | 0.90 | Preview appears to be call-opening or logistics text rather than evidence. |
| amzn_2024_aws_metadata | `AMZN_2024_Q4.0_r40_c8` | rejected | 0.90 | Preview appears to be call-opening or logistics text rather than evidence. |
| googl_2023_advertising_metadata | `GOOGL_2023_Q1.0_r53_c0` | rejected | 0.90 | Preview appears to be call-opening or logistics text rather than evidence. |
| googl_2024_advertising | `GOOGL_2024_Q4.0_r60_c10` | accepted | 0.85 | Preview contains the required target terms and is not call-opening boilerplate. |
| googl_ads_vs_meta_ads_2024 | `META_2024_Q1.0_r77_c11` | rejected | 0.75 | Preview does not directly support the matched target; missing advertising. |
| googl_ads_vs_meta_ads_2024 | `META_2024_Q4.0_r80_c18` | rejected | 0.75 | Preview does not directly support the matched target; missing advertising. |
| meta_2023_advertising_metadata | `META_2023_Q4.0_r76_c18` | accepted | 0.85 | Preview contains the required target terms and is not call-opening boilerplate. |
| meta_2024_advertising | `META_2024_Q1.0_r77_c12` | accepted | 0.85 | Preview contains the required target terms and is not call-opening boilerplate. |
| meta_2024_advertising | `META_2024_Q4.0_r80_c18` | rejected | 0.75 | Preview does not directly support the matched target; missing advertising. |
| msft_2023_cloud | `MSFT_2023_Q3.0_r96_c0` | rejected | 0.90 | Preview appears to be call-opening or logistics text rather than evidence. |
| msft_2023_cloud | `MSFT_2023_Q3.0_r96_c15` | accepted | 0.85 | Preview contains the required target terms and is not call-opening boilerplate. |
| msft_2024_azure_metadata | `MSFT_2024_Q3.0_r100_c1` | rejected | 0.75 | Preview does not directly support the matched target; missing azure. |
| msft_2024_azure_metadata | `MSFT_2024_Q3.0_r100_c14` | accepted | 0.85 | Preview contains the required target terms and is not call-opening boilerplate. |
| msft_2024_cloud | `MSFT_2024_Q2.0_r99_c0` | rejected | 0.90 | Preview appears to be call-opening or logistics text rather than evidence. |
| msft_2024_cloud | `MSFT_2024_Q3.0_r100_c0` | rejected | 0.90 | Preview appears to be call-opening or logistics text rather than evidence. |
| msft_2024_cloud | `MSFT_2024_Q3.0_r100_c12` | rejected | 0.75 | Preview does not directly support the matched target; missing cloud. |
| msft_cloud_2023_vs_2024 | `MSFT_2023_Q3.0_r96_c0` | rejected | 0.90 | Preview appears to be call-opening or logistics text rather than evidence. |
| msft_cloud_2023_vs_2024 | `MSFT_2024_Q2.0_r99_c0` | rejected | 0.90 | Preview appears to be call-opening or logistics text rather than evidence. |
| msft_cloud_2023_vs_2024 | `MSFT_2024_Q3.0_r100_c0` | rejected | 0.90 | Preview appears to be call-opening or logistics text rather than evidence. |
| msft_cloud_vs_amzn_aws_2023 | `MSFT_2023_Q2.0_r95_c15` | accepted | 0.85 | Preview contains the required target terms and is not call-opening boilerplate. |
| msft_cloud_vs_amzn_aws_2023 | `MSFT_2023_Q3.0_r96_c0` | rejected | 0.90 | Preview appears to be call-opening or logistics text rather than evidence. |
| msft_cloud_vs_amzn_aws_2023 | `MSFT_2023_Q3.0_r96_c1` | accepted | 0.85 | Preview contains the required target terms and is not call-opening boilerplate. |
| nvda_2023_data_center | `NVDA_2023_Q2.0_r115_c7` | rejected | 0.75 | Preview does not directly support the matched target; missing center, data. |
| nvda_2023_data_center | `NVDA_2023_Q3.0_r116_c1` | accepted | 0.85 | Preview contains the required target terms and is not call-opening boilerplate. |
| nvda_2023_data_center | `NVDA_2023_Q3.0_r116_c17` | rejected | 0.75 | Preview does not directly support the matched target; missing center, data. |
| nvda_2024_data_center | `NVDA_2024_Q1.0_r118_c0` | rejected | 0.90 | Preview appears to be call-opening or logistics text rather than evidence. |
| nvda_2024_data_center | `NVDA_2024_Q1.0_r118_c1` | accepted | 0.85 | Preview contains the required target terms and is not call-opening boilerplate. |
| nvda_2024_data_center | `NVDA_2024_Q1.0_r118_c6` | rejected | 0.75 | Preview does not directly support the matched target; missing center, data. |
| nvda_data_center_2023_vs_2024 | `NVDA_2023_Q1.0_r114_c0` | rejected | 0.90 | Preview appears to be call-opening or logistics text rather than evidence. |
| nvda_data_center_2023_vs_2024 | `NVDA_2024_Q1.0_r118_c6` | rejected | 0.75 | Preview does not directly support the matched target; missing center, data. |
| tsla_2023_margin_comment | `TSLA_2023_Q2.0_r133_c16` | rejected | 0.75 | Preview does not directly support the matched target; missing margin. |
| tsla_2023_margin_comment | `TSLA_2023_Q3.0_r134_c11` | rejected | 0.75 | Preview does not directly support the matched target; missing margin. |
| tsla_2024_margin_comment | `TSLA_2024_Q1.0_r136_c6` | rejected | 0.75 | Preview does not directly support the matched target; missing margin. |
| tsla_margin_2023_vs_2024 | `TSLA_2023_Q2.0_r133_c16` | rejected | 0.75 | Preview does not directly support the matched target; missing margin. |
| tsla_margin_vs_nvda_data_center_2024 | `NVDA_2024_Q1.0_r118_c6` | rejected | 0.75 | Preview does not directly support the matched target; missing center, data. |
| tsla_margin_vs_nvda_data_center_2024 | `NVDA_2024_Q2.0_r119_c1` | accepted | 0.85 | Preview contains the required target terms and is not call-opening boilerplate. |
