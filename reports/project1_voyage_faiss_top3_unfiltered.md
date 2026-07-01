# Retrieval Evaluation Report

## Run Overview

| Field | Value |
|---|---|
| Metrics | Precision@3, Recall@3, Hit@3, MRR@3 |
| Cases scored | 24 |
| Providers | voyage-faiss |
| Case categories | comparison; metadata_filtered; multi_hop; simple |
| Cases with missed targets or runtime errors | 11 |

```mermaid
flowchart LR
    A["Eval cases"] --> B["Retrieval run JSONL"]
    B --> C["Retrieval metrics"]
    C --> D["Benchmark summary"]
    C --> E["Failure analysis"]
```

## Benchmark Summary

| Provider | Case Type | Cases | Precision@K | Recall@K | Hit@K | MRR@K | Runtime Errors |
|---|---|---:|---:|---:|---:|---:|---:|
| voyage-faiss | comparison | 4 | 0.417 | 0.500 | 1.000 | 0.583 | 0 |
| voyage-faiss | metadata_filtered | 6 | 0.389 | 0.667 | 0.667 | 0.361 | 0 |
| voyage-faiss | multi_hop | 4 | 0.583 | 0.750 | 1.000 | 0.875 | 0 |
| voyage-faiss | simple | 10 | 0.333 | 0.700 | 0.700 | 0.600 | 0 |

## Failure Analysis

Cases below missed at least one expected evidence target or produced a runtime error.

| Case | Provider | Category | Recall@K | Hit@K | Covered Targets | Missed Targets / Error |
|---|---|---|---:|---:|---|---|
| aapl_2023_services_revenue | voyage-faiss | simple | 0.000 | 0.000 | - | AAPL 2023 services revenue |
| tsla_2024_margin_comment | voyage-faiss | simple | 0.000 | 0.000 | - | TSLA 2024 margin |
| amzn_2023_aws | voyage-faiss | simple | 0.000 | 0.000 | - | AMZN 2023 aws |
| meta_2023_advertising_metadata | voyage-faiss | metadata_filtered | 0.000 | 0.000 | - | META 2023 advertising |
| tsla_2024_profitability_metadata | voyage-faiss | metadata_filtered | 0.000 | 0.000 | - | TSLA 2024 profitability |
| aapl_services_2023_vs_2024 | voyage-faiss | multi_hop | 0.500 | 1.000 | AAPL 2024 services revenue | AAPL 2023 services revenue |
| tsla_margin_2023_vs_2024 | voyage-faiss | multi_hop | 0.500 | 1.000 | TSLA 2023 margin | TSLA 2024 margin |
| msft_cloud_vs_amzn_aws_2023 | voyage-faiss | comparison | 0.500 | 1.000 | MSFT 2023 cloud | AMZN 2023 AWS |
| googl_ads_vs_meta_ads_2024 | voyage-faiss | comparison | 0.500 | 1.000 | META 2024 advertising | GOOGL 2024 advertising |
| aapl_services_vs_msft_cloud_2024 | voyage-faiss | comparison | 0.500 | 1.000 | AAPL 2024 services | MSFT 2024 cloud |
| tsla_margin_vs_nvda_data_center_2024 | voyage-faiss | comparison | 0.500 | 1.000 | NVDA 2024 data center | TSLA 2024 margin |

## Case Results

| Case | Provider | Category | Precision@K | Recall@K | Hit@K | RR@K | Evidence Targets Covered |
|---|---|---|---:|---:|---:|---:|---:|
| aapl_2023_services_revenue | voyage-faiss | simple | 0.000 | 0.000 | 0.000 | 0.000 | 0/1 |
| tsla_2024_margin_comment | voyage-faiss | simple | 0.000 | 0.000 | 0.000 | 0.000 | 0/1 |
| nvda_2024_data_center | voyage-faiss | simple | 0.333 | 1.000 | 1.000 | 1.000 | 1/1 |
| msft_2024_cloud | voyage-faiss | simple | 0.667 | 1.000 | 1.000 | 1.000 | 1/1 |
| amzn_2023_aws | voyage-faiss | simple | 0.000 | 0.000 | 0.000 | 0.000 | 0/1 |
| meta_2024_advertising | voyage-faiss | simple | 0.333 | 1.000 | 1.000 | 1.000 | 1/1 |
| googl_2024_advertising | voyage-faiss | simple | 0.333 | 1.000 | 1.000 | 0.500 | 1/1 |
| msft_2023_cloud | voyage-faiss | simple | 0.333 | 1.000 | 1.000 | 0.500 | 1/1 |
| tsla_2023_margin_comment | voyage-faiss | simple | 0.667 | 1.000 | 1.000 | 1.000 | 1/1 |
| nvda_2023_data_center | voyage-faiss | simple | 0.667 | 1.000 | 1.000 | 1.000 | 1/1 |
| aapl_2024_services_metadata | voyage-faiss | metadata_filtered | 1.000 | 1.000 | 1.000 | 1.000 | 1/1 |
| amzn_2024_aws_metadata | voyage-faiss | metadata_filtered | 0.667 | 1.000 | 1.000 | 0.500 | 1/1 |
| meta_2023_advertising_metadata | voyage-faiss | metadata_filtered | 0.000 | 0.000 | 0.000 | 0.000 | 0/1 |
| googl_2023_advertising_metadata | voyage-faiss | metadata_filtered | 0.333 | 1.000 | 1.000 | 0.333 | 1/1 |
| msft_2024_azure_metadata | voyage-faiss | metadata_filtered | 0.333 | 1.000 | 1.000 | 0.333 | 1/1 |
| tsla_2024_profitability_metadata | voyage-faiss | metadata_filtered | 0.000 | 0.000 | 0.000 | 0.000 | 0/1 |
| aapl_services_2023_vs_2024 | voyage-faiss | multi_hop | 0.333 | 0.500 | 1.000 | 1.000 | 1/2 |
| tsla_margin_2023_vs_2024 | voyage-faiss | multi_hop | 0.333 | 0.500 | 1.000 | 0.500 | 1/2 |
| nvda_data_center_2023_vs_2024 | voyage-faiss | multi_hop | 0.667 | 1.000 | 1.000 | 1.000 | 2/2 |
| msft_cloud_2023_vs_2024 | voyage-faiss | multi_hop | 1.000 | 1.000 | 1.000 | 1.000 | 2/2 |
| msft_cloud_vs_amzn_aws_2023 | voyage-faiss | comparison | 0.333 | 0.500 | 1.000 | 0.500 | 1/2 |
| googl_ads_vs_meta_ads_2024 | voyage-faiss | comparison | 0.667 | 0.500 | 1.000 | 0.500 | 1/2 |
| aapl_services_vs_msft_cloud_2024 | voyage-faiss | comparison | 0.333 | 0.500 | 1.000 | 0.333 | 1/2 |
| tsla_margin_vs_nvda_data_center_2024 | voyage-faiss | comparison | 0.333 | 0.500 | 1.000 | 1.000 | 1/2 |
