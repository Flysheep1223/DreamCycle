"""Shared typed contracts used by routing, judging, OCR and aggregation."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TaskMode(str, Enum):
    TEXT_TO_IMAGE = "text_to_image"
    IMAGE_EDITING = "image_editing"
    REFERENCE_GENERATION = "reference_generation"


class CheckItem(BaseModel):
    id: str
    question: str
    expected: str = "yes"


class RouteDecision(BaseModel):
    modes: list[TaskMode] = Field(min_length=1)
    needs_ocr: bool = False
    needs_control: bool = False
    no_extra_text: bool = False
    multi_reference: bool = False
    input_warnings: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0, le=1)
    reason: str = ""
    target_texts: list[str] = Field(default_factory=list)
    task_checklist: list[CheckItem] = Field(default_factory=list)
    preservation_checklist: list[CheckItem] = Field(default_factory=list)


class JudgeCheckResult(BaseModel):
    id: str
    question: str = ""
    score: float = Field(ge=0, le=1)
    reason: str = ""


class EditScore(BaseModel):
    sc: float = Field(ge=0, le=10)
    pq: float = Field(ge=0, le=10)


class ReferenceScore(BaseModel):
    cp: float = Field(ge=0, le=4)
    pf: float = Field(ge=0, le=4)


class JudgeResult(BaseModel):
    task_score: float = Field(ge=0, le=1)
    preservation_score: float | None = Field(default=None, ge=0, le=1)
    text_layout_score: float | None = Field(default=None, ge=0, le=1)
    pq: float = Field(ge=0, le=10)
    checks: list[JudgeCheckResult] = Field(default_factory=list)
    edit: EditScore | None = None
    reference: ReferenceScore | None = None
    failure_tags: list[str] = Field(default_factory=list)


class OCRScore(BaseModel):
    accuracy: float = Field(ge=0, le=1)
    ned: float = Field(ge=0, le=1)
    cer: float = Field(ge=0)
    f1: float = Field(ge=0, le=1)
    precision: float = Field(ge=0, le=1)
    recall: float = Field(ge=0, le=1)
    targets: list[dict[str, Any]] = Field(default_factory=list)
    predictions: list[str] = Field(default_factory=list)
    skipped_reason: str | None = None


class GeneratedImage(BaseModel):
    path: str
    url: str | None = None
    size: str | None = None


class AdviceReport(BaseModel):
    generation_prompt_suggestions: list[str] = Field(default_factory=list)
    revised_generation_prompt: str = ""
    overall_assessment: str
    evaluation_prompt_suggestions: list[str] = Field(default_factory=list)
    additional_checks: list[CheckItem] = Field(default_factory=list)
    possible_judge_errors: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class EvaluationResult(BaseModel):
    image: GeneratedImage
    modes: list[TaskMode]
    metrics: dict[str, Any] = Field(default_factory=dict)
    full_requirement_rate: float | None = None
    minimum_requirement_score: float | None = None
    raw_scores: dict[str, Any]
    advice: AdviceReport | None = None
    failure_tags: list[str] = Field(default_factory=list)


class PipelineResult(BaseModel):
    run_id: str
    route: RouteDecision
    evaluations: list[EvaluationResult]
    output_dir: str
