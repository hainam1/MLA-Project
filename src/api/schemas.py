"""Typed request and response contracts for the HTTP API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProcessRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vietnamese_vocabulary: str = Field(min_length=1, max_length=100)
    target_level: Literal["A1", "A2", "B1", "B2", "C1"]

    @field_validator("vietnamese_vocabulary")
    @classmethod
    def reject_whitespace_only(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("vietnamese_vocabulary must not be blank")
        return value


class PipelineResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    status: Literal["success", "error"]
    input_vi: str | None = None
    route: str | None = None
    requested_level: str | None = None
    baseline_translation_en: str | None = None
    translation_en: str | None = None
    meaning_analysis: dict[str, Any] | None = None
    selected_vocabulary: dict[str, Any] | None = None
    cefr: dict[str, Any] | None = None
    generated_example: dict[str, Any] | None = None
    capabilities: dict[str, bool] | None = None


class ErrorBody(BaseModel):
    code: str
    message: str
    request_id: str
    details: Any | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody
