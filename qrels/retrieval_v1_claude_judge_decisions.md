# Qrels Judge Decisions

These decisions were produced by an independent qrels judge. They are useful for exercising the judge-review workflow and should be spot-checked before being treated as production benchmark labels.

## Rubric

| Version | `claude-relevance-rubric-v1` |
|---|---|
| Judge model | `claude-sonnet-5` |

## Summary

| Decisions | Accepted | Rejected |
|---:|---:|---:|
| 49 | 14 | 35 |

## Decisions

| Case | Chunk ID | Decision | Confidence | Rationale |
|---|---|---|---:|---|
| aapl_2023_services_revenue | `AAPL_2023_Q1.0_r12_c2` | rejected | 0.85 | The chunk discusses iPad and Wearables revenue, not Services revenue, and thus does not directly support the matched target. |
| aapl_2023_services_revenue | `AAPL_2023_Q4.0_r15_c18` | rejected | 0.85 | This chunk is an analyst's question referencing Services revenue in passing, not a substantive comment or data point on Apple's 2023 services revenue itself. |
| aapl_2024_services_metadata | `AAPL_2024_Q2.0_r17_c0` | rejected | 0.97 | The chunk is only call-opening boilerplate and does not mention services revenue figures or discussion. |
| aapl_2024_services_metadata | `AAPL_2024_Q4.0_r19_c0` | rejected | 0.97 | This chunk is only call-opening boilerplate introducing speakers and does not contain any services revenue figures or discussion. |
| aapl_2024_services_metadata | `AAPL_2024_Q4.0_r19_c10` | rejected | 0.92 | The chunk discusses iPhone revenue growth expectations, not services revenue, and thus does not directly support the matched target. |
| aapl_services_2023_vs_2024 | `AAPL_2024_Q4.0_r19_c10` | rejected | 0.90 | The chunk discusses iPhone revenue growth expectations, not services revenue, so it does not support the AAPL 2024 services revenue target. |
| aapl_services_vs_msft_cloud_2024 | `AAPL_2024_Q3.0_r18_c11` | accepted | 0.90 | The chunk directly discusses Apple's Services segment growth and performance commentary, matching the AAPL 2024 services target. |
| aapl_services_vs_msft_cloud_2024 | `AAPL_2024_Q4.0_r19_c10` | rejected | 0.92 | The chunk discusses iPhone revenue growth expectations, not Apple services performance, so it does not directly support the AAPL 2024 services target. |
| aapl_services_vs_msft_cloud_2024 | `MSFT_2024_Q3.0_r100_c0` | rejected | 0.97 | The chunk is only call-opening operator boilerplate and contains no actual cloud commentary from Microsoft. |
| amzn_2023_aws | `AMZN_2023_Q3.0_r35_c11` | rejected | 0.65 | The chunk discusses Amazon Business and enterprise procurement, not AWS specifically, so it does not directly support the AWS target. |
| amzn_2023_aws | `AMZN_2023_Q4.0_r36_c14` | accepted | 0.85 | The chunk directly discusses AWS-related topics (Trainium, Inferentia, CodeWhisperer) as examples of AWS customer adoption and product offerings in 2023, directly supporting the AWS comment target. |
| amzn_2023_aws | `AMZN_2023_Q4.0_r36_c15` | rejected | 0.85 | The chunk is an analyst question about IT budget cycles and AI vs. optimization themes for 2024, not a substantive comment on AWS 2023 performance or results. |
| amzn_2024_aws_metadata | `AMZN_2024_Q1.0_r37_c8` | rejected | 0.85 | The chunk discusses overall free cash flow, capital investments, and segment operating income without directly addressing AWS-specific evidence. |
| amzn_2024_aws_metadata | `AMZN_2024_Q3.0_r39_c0` | rejected | 0.95 | The chunk is merely call-opening operator boilerplate and contains no substantive AWS discussion. |
| amzn_2024_aws_metadata | `AMZN_2024_Q4.0_r40_c8` | accepted | 0.85 | The chunk directly discusses AWS operating margins for Amazon, matching the AMZN 2024 AWS target. |
| googl_2023_advertising_metadata | `GOOGL_2023_Q1.0_r53_c0` | rejected | 0.95 | The chunk is call-opening boilerplate/operator introduction with no substantive discussion of Alphabet advertising performance or metrics. |
| googl_2024_advertising | `GOOGL_2024_Q4.0_r60_c10` | accepted | 0.85 | The chunk directly discusses 2024 advertising revenue growth dynamics and headwinds, matching the target on GOOGL 2024 advertising. |
| googl_ads_vs_meta_ads_2024 | `META_2024_Q1.0_r77_c11` | rejected | 0.85 | The chunk discusses AI infrastructure investment and tax guidance, not advertising commentary, so it does not directly support the META 2024 advertising target. |
| googl_ads_vs_meta_ads_2024 | `META_2024_Q4.0_r80_c18` | rejected | 0.85 | The chunk discusses Reality Labs and general product philosophy rather than providing substantive Meta advertising commentary. |
| meta_2023_advertising_metadata | `META_2023_Q4.0_r76_c18` | accepted | 0.85 | The chunk discusses Meta's advertising revenue trends specifically related to Chinese advertisers, directly supporting the META 2023 advertising target. |
| meta_2024_advertising | `META_2024_Q1.0_r77_c12` | accepted | 0.85 | The chunk discusses Meta's advertising tools and features (Conversions API, AEM) and positive advertiser feedback, directly supporting the target of Meta 2024 advertising commentary. |
| meta_2024_advertising | `META_2024_Q4.0_r80_c18` | rejected | 0.92 | The chunk discusses consumer experience focus and Reality Labs expectations, not advertising revenue or ad demand. |
| msft_2023_cloud | `MSFT_2023_Q3.0_r96_c0` | rejected | 0.97 | This chunk is only call-opening boilerplate and operator/IR introduction, containing no substantive cloud or Azure commentary. |
| msft_2023_cloud | `MSFT_2023_Q3.0_r96_c15` | accepted | 0.85 | The chunk directly discusses Azure and the Copilot stack availability on Azure, providing direct evidence of Microsoft's 2023 cloud/Azure commentary. |
| msft_2024_azure_metadata | `MSFT_2024_Q3.0_r100_c1` | rejected | 0.75 | The chunk discusses overall annual revenue and Microsoft Cloud revenue but does not mention Azure specifically, so it fails to directly support the Azure evidence target despite matching year metadata. |
| msft_2024_azure_metadata | `MSFT_2024_Q3.0_r100_c14` | accepted | 0.85 | The chunk directly discusses Azure workload growth and enterprise adoption with correct MSFT 2024 metadata, matching the target. |
| msft_2024_cloud | `MSFT_2024_Q2.0_r99_c0` | rejected | 0.97 | The chunk is only call-opening operator boilerplate and contains no substantive Azure or cloud commentary. |
| msft_2024_cloud | `MSFT_2024_Q3.0_r100_c0` | rejected | 0.97 | This chunk is only call-opening operator boilerplate and contains no actual cloud or Azure commentary. |
| msft_2024_cloud | `MSFT_2024_Q3.0_r100_c12` | accepted | 0.70 | The chunk discusses scaling cloud/AI infrastructure spend based on demand signals, which directly relates to Microsoft's 2024 cloud commentary on capacity and growth strategy. |
| msft_cloud_2023_vs_2024 | `MSFT_2023_Q3.0_r96_c0` | rejected | 0.97 | This chunk is only call-opening boilerplate and operator/IR introduction with no actual cloud commentary or financial content. |
| msft_cloud_2023_vs_2024 | `MSFT_2024_Q2.0_r99_c0` | rejected | 0.97 | This chunk is only call-opening operator boilerplate with no actual cloud commentary or financial content. |
| msft_cloud_2023_vs_2024 | `MSFT_2024_Q3.0_r100_c0` | rejected | 0.97 | This chunk is only call-opening operator boilerplate with no actual cloud revenue or growth commentary. |
| msft_cloud_vs_amzn_aws_2023 | `MSFT_2023_Q2.0_r95_c15` | accepted | 0.65 | The chunk discusses Microsoft's public cloud cost optimization and workload commentary, directly relevant to the MSFT 2023 cloud target. |
| msft_cloud_vs_amzn_aws_2023 | `MSFT_2023_Q3.0_r96_c0` | rejected | 0.97 | This chunk is only call-opening boilerplate and operator/IR introduction with no substantive cloud commentary. |
| msft_cloud_vs_amzn_aws_2023 | `MSFT_2023_Q3.0_r96_c1` | accepted | 0.95 | The chunk directly reports Microsoft Cloud's 2023 annual revenue and growth rate, matching the MSFT 2023 cloud target. |
| nvda_2023_data_center | `NVDA_2023_Q2.0_r115_c7` | rejected | 0.60 | The chunk discusses supply chain lead times and TSMC commitments rather than directly commenting on data center demand. |
| nvda_2023_data_center | `NVDA_2023_Q3.0_r116_c1` | accepted | 0.92 | The chunk explicitly states tremendous demand for NVIDIA's data center accelerated computing and AI platforms in 2023, directly supporting the target. |
| nvda_2023_data_center | `NVDA_2023_Q3.0_r116_c17` | rejected | 0.75 | The chunk is Jensen Huang's generic closing remarks about a 'new computing era' and platform transitions, not a specific comment on 2023 data center demand. |
| nvda_2024_data_center | `NVDA_2024_Q1.0_r118_c0` | rejected | 0.97 | This chunk is purely call-opening operator boilerplate with no mention of data center demand or financial content. |
| nvda_2024_data_center | `NVDA_2024_Q1.0_r118_c1` | accepted | 0.95 | The chunk directly reports NVDA's 2024 Q4 data center revenue growth and demand driver (Hopper GPU platform), matching the requested demand comment target. |
| nvda_2024_data_center | `NVDA_2024_Q1.0_r118_c6` | rejected | 0.95 | The chunk only discusses upcoming investor conference logistics, not any Nvidia data center demand commentary. |
| nvda_data_center_2023_vs_2024 | `NVDA_2023_Q1.0_r114_c0` | rejected | 0.97 | This chunk is only call-opening boilerplate and operator introductions with no discussion of data center demand. |
| nvda_data_center_2023_vs_2024 | `NVDA_2024_Q1.0_r118_c6` | rejected | 0.95 | The chunk is call-closing boilerplate about upcoming investor events and financial details on the IR website, with no substantive commentary on data center demand. |
| tsla_2023_margin_comment | `TSLA_2023_Q2.0_r133_c16` | rejected | 0.85 | The chunk discusses vehicle affordability and demand factors, not Tesla's gross margin or profitability directly. |
| tsla_2023_margin_comment | `TSLA_2023_Q3.0_r134_c11` | rejected | 0.95 | The chunk is a generic buy-low-sell-high commentary with no mention of Tesla's gross margin or profitability metrics. |
| tsla_2024_margin_comment | `TSLA_2024_Q1.0_r136_c6` | rejected | 0.97 | The chunk discusses shareholder governance issues (ISS, Glass Lewis, activists) and does not address Tesla's gross margin or profitability drivers in 2024. |
| tsla_margin_2023_vs_2024 | `TSLA_2023_Q2.0_r133_c16` | rejected | 0.75 | The chunk discusses vehicle affordability and demand due to interest rates, not Tesla's gross margin or profitability metrics. |
| tsla_margin_vs_nvda_data_center_2024 | `NVDA_2024_Q1.0_r118_c6` | rejected | 0.95 | The chunk is call-closing boilerplate about upcoming events and IR logistics, not substantive data center demand commentary. |
| tsla_margin_vs_nvda_data_center_2024 | `NVDA_2024_Q2.0_r119_c1` | accepted | 0.95 | The chunk directly discusses NVIDIA's 2024 data center revenue growth and demand drivers, matching the target 'NVDA 2024 data center'. |
