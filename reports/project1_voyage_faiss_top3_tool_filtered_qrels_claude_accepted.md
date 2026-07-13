# Retrieval Evaluation Report

## Run Overview

| Field | Value |
|---|---|
| Metrics | Precision@3, Recall@3, Hit@3, MRR@3 |
| Label source | qrels:accepted |
| Cases scored | 24 |
| Providers | voyage-faiss-filtered |
| Case categories | comparison; metadata_filtered; multi_hop; simple |
| Cases with no relevant labels | 11 |
| Cases with missed targets or runtime errors | 0 |

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
| voyage-faiss-filtered | comparison | 4 | 0.333 | 0.750 | 0.750 | 0.458 | 0 |
| voyage-faiss-filtered | metadata_filtered | 6 | 0.167 | 0.500 | 0.500 | 0.306 | 0 |
| voyage-faiss-filtered | multi_hop | 4 | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| voyage-faiss-filtered | simple | 10 | 0.233 | 0.700 | 0.700 | 0.350 | 0 |

## Failure Analysis

Cases below missed at least one expected evidence target or produced a runtime error.

| Case | Provider | Category | Recall@K | Hit@K | Covered Targets | Missed Targets / Error |
|---|---|---|---:|---:|---|---|
| _None_ |  |  |  |  |  |

## Unlabeled Cases

Cases below have zero relevant labels for the selected label source.

| Case | Provider | Category |
|---|---|---|
| aapl_2023_services_revenue | voyage-faiss-filtered | simple |
| tsla_2024_margin_comment | voyage-faiss-filtered | simple |
| tsla_2023_margin_comment | voyage-faiss-filtered | simple |
| aapl_2024_services_metadata | voyage-faiss-filtered | metadata_filtered |
| googl_2023_advertising_metadata | voyage-faiss-filtered | metadata_filtered |
| tsla_2024_profitability_metadata | voyage-faiss-filtered | metadata_filtered |
| aapl_services_2023_vs_2024 | voyage-faiss-filtered | multi_hop |
| tsla_margin_2023_vs_2024 | voyage-faiss-filtered | multi_hop |
| nvda_data_center_2023_vs_2024 | voyage-faiss-filtered | multi_hop |
| msft_cloud_2023_vs_2024 | voyage-faiss-filtered | multi_hop |
| googl_ads_vs_meta_ads_2024 | voyage-faiss-filtered | comparison |

## Case Results

| Case | Provider | Category | Precision@K | Recall@K | Hit@K | RR@K | Evidence Targets Covered |
|---|---|---|---:|---:|---:|---:|---:|
| aapl_2023_services_revenue | voyage-faiss-filtered | simple | 0.000 | 0.000 | 0.000 | 0.000 | 0/0 |
| tsla_2024_margin_comment | voyage-faiss-filtered | simple | 0.000 | 0.000 | 0.000 | 0.000 | 0/0 |
| nvda_2024_data_center | voyage-faiss-filtered | simple | 0.333 | 1.000 | 1.000 | 0.500 | 1/1 |
| msft_2024_cloud | voyage-faiss-filtered | simple | 0.333 | 1.000 | 1.000 | 0.500 | 1/1 |
| amzn_2023_aws | voyage-faiss-filtered | simple | 0.333 | 1.000 | 1.000 | 1.000 | 1/1 |
| meta_2024_advertising | voyage-faiss-filtered | simple | 0.333 | 1.000 | 1.000 | 0.333 | 1/1 |
| googl_2024_advertising | voyage-faiss-filtered | simple | 0.333 | 1.000 | 1.000 | 0.500 | 1/1 |
| msft_2023_cloud | voyage-faiss-filtered | simple | 0.333 | 1.000 | 1.000 | 0.333 | 1/1 |
| tsla_2023_margin_comment | voyage-faiss-filtered | simple | 0.000 | 0.000 | 0.000 | 0.000 | 0/0 |
| nvda_2023_data_center | voyage-faiss-filtered | simple | 0.333 | 1.000 | 1.000 | 0.333 | 1/1 |
| aapl_2024_services_metadata | voyage-faiss-filtered | metadata_filtered | 0.000 | 0.000 | 0.000 | 0.000 | 0/0 |
| amzn_2024_aws_metadata | voyage-faiss-filtered | metadata_filtered | 0.333 | 1.000 | 1.000 | 1.000 | 1/1 |
| meta_2023_advertising_metadata | voyage-faiss-filtered | metadata_filtered | 0.333 | 1.000 | 1.000 | 0.500 | 1/1 |
| googl_2023_advertising_metadata | voyage-faiss-filtered | metadata_filtered | 0.000 | 0.000 | 0.000 | 0.000 | 0/0 |
| msft_2024_azure_metadata | voyage-faiss-filtered | metadata_filtered | 0.333 | 1.000 | 1.000 | 0.333 | 1/1 |
| tsla_2024_profitability_metadata | voyage-faiss-filtered | metadata_filtered | 0.000 | 0.000 | 0.000 | 0.000 | 0/0 |
| aapl_services_2023_vs_2024 | voyage-faiss-filtered | multi_hop | 0.000 | 0.000 | 0.000 | 0.000 | 0/0 |
| tsla_margin_2023_vs_2024 | voyage-faiss-filtered | multi_hop | 0.000 | 0.000 | 0.000 | 0.000 | 0/0 |
| nvda_data_center_2023_vs_2024 | voyage-faiss-filtered | multi_hop | 0.000 | 0.000 | 0.000 | 0.000 | 0/0 |
| msft_cloud_2023_vs_2024 | voyage-faiss-filtered | multi_hop | 0.000 | 0.000 | 0.000 | 0.000 | 0/0 |
| msft_cloud_vs_amzn_aws_2023 | voyage-faiss-filtered | comparison | 0.667 | 1.000 | 1.000 | 0.500 | 2/2 |
| googl_ads_vs_meta_ads_2024 | voyage-faiss-filtered | comparison | 0.000 | 0.000 | 0.000 | 0.000 | 0/0 |
| aapl_services_vs_msft_cloud_2024 | voyage-faiss-filtered | comparison | 0.333 | 1.000 | 1.000 | 1.000 | 1/1 |
| tsla_margin_vs_nvda_data_center_2024 | voyage-faiss-filtered | comparison | 0.333 | 1.000 | 1.000 | 0.333 | 1/1 |
