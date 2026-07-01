from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RelevanceCriteria(BaseModel):
    """Inspectable relevance label based on metadata and required text terms."""

    tickers: list[str] = Field(default_factory=list)
    years: list[int] = Field(default_factory=list)
    required_terms: list[str] = Field(default_factory=list)


class RelevanceTarget(RelevanceCriteria):
    """One evidence target that should be covered by retrieved chunks."""

    label: str = ""


class EvalCase(BaseModel):
    id: str
    question: str
    category: str
    expected_tickers: list[str] = Field(default_factory=list)
    expected_years: list[int] = Field(default_factory=list)
    relevant_chunk_ids: list[str] = Field(default_factory=list)
    relevance_criteria: RelevanceCriteria = Field(default_factory=RelevanceCriteria)
    relevance_targets: list[RelevanceTarget] = Field(default_factory=list)
    notes: str = ""


class RetrievedChunk(BaseModel):
    chunk_id: str
    rank: int = Field(ge=1)
    score: float | None = None
    text: str = ""
    ticker: str | None = None
    year: int | None = None
    quarter: str | None = None


class RetrievalRunCase(BaseModel):
    case_id: str
    provider: str = "unknown"
    retrieved_chunks: list[RetrievedChunk]
    runtime_error: str | None = None


class CaseMetricResult(BaseModel):
    case_id: str
    category: str
    provider: str
    k: int
    precision_at_k: float
    recall_at_k: float
    hit_at_k: float
    reciprocal_rank_at_k: float
    relevant_retrieved: int
    retrieved_at_k: int
    total_relevant: int
    covered_targets: list[str] = Field(default_factory=list)
    missed_targets: list[str] = Field(default_factory=list)
    runtime_error: str | None = None


class ReportSummaryRow(BaseModel):
    provider: str
    category: str
    cases: int
    precision_at_k: float
    recall_at_k: float
    hit_at_k: float
    mrr_at_k: float
    runtime_errors: int


class EvalReport(BaseModel):
    metric_type: Literal["retrieval"] = "retrieval"
    k: int
    case_results: list[CaseMetricResult]
    summary: list[ReportSummaryRow]