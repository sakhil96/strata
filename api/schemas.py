"""Pydantic schemas for the STRATA API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    persona: str = Field(default="EXECUTIVE_ROLE")


class QueryRequest(BaseModel):
    view: str = Field(default="SCM_GOVERNED_V1")
    metrics: list[str] = Field(..., min_length=1)
    dimensions: list[str] = Field(default_factory=list)
    time: dict = Field(default_factory=dict)
    filters: list[dict] = Field(default_factory=list)


class CompareRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    personas: list[str] = Field(default=["PLANNING_ROLE", "PROCUREMENT_ROLE", "LOGISTICS_ROLE"])


class BeforeAfterRequest(BaseModel):
    metric: str
    dimensions: list[str] = Field(default_factory=list)
    before_time: dict = Field(...)
    after_time: dict = Field(...)


class AnswerContract(BaseModel):
    metric_name: str | None = None
    definition: str | None = None
    canonical_query: dict | None = None
    semantic_query_hash: str | None = None
    sql: str | None = None
    lineage: dict | None = None
    role: str | None = None
    latency_ms: int | None = None
    rows: list[dict] = Field(default_factory=list)
    row_count: int = 0
    error: str | None = None
