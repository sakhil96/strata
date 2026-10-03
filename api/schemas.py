from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Persona = Literal["PLANNING_ROLE", "PROCUREMENT_ROLE", "LOGISTICS_ROLE", "EXECUTIVE_ROLE", "EMEA_PLANNING_ROLE", "JUDGE_ROLE"]
Name = Field(pattern=r"^[a-z][a-z0-9_]{1,63}$")


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TimeWindow(Strict):
    range: str | None = Field(default=None, pattern=r"^[a-z0-9_]{2,24}$")
    start: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    end: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")


class Filter(Strict):
    dimension: str = Name
    operator: Literal["=", "!=", "in"] = "="
    value: str | list[str] = Field(max_length=40)


class SemanticQuery(Strict):
    metrics: list[str] = Field(min_length=1, max_length=4)
    dimensions: list[str] = Field(default_factory=list, max_length=4)
    time: TimeWindow = Field(default_factory=TimeWindow)
    filters: list[Filter] = Field(default_factory=list, max_length=6)


class AskRequest(Strict):
    question: str = Field(min_length=3, max_length=500)
    persona: Persona | None = None
    thread_id: int | None = Field(default=None, ge=0)
    parent_message_id: int | None = Field(default=None, ge=0)


class QueryRequest(Strict):
    query: SemanticQuery
    persona: Persona | None = None


class CompareRequest(Strict):
    question: str | None = Field(default=None, min_length=3, max_length=500)
    phrasings: dict[Persona, str] | None = None
    query: SemanticQuery | None = None


class BeforeAfterRequest(Strict):
    window: str = Field(default="fy2026", pattern=r"^[a-z0-9_]{2,24}$")
