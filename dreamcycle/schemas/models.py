"""Shared typed contracts used by routing, judging, OCR and aggregation."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class TaskMode(str, Enum):
    TEXT_TO_IMAGE = "text_to_image"
    IMAGE_EDITING = "image_editing"
    REFERENCE_GENERATION = "reference_generation"


class ActionRegion(BaseModel):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)


class ActionSpec(BaseModel):
    subject: str
    target: str
    expected_direction: Literal["toward", "away"]
    region: ActionRegion | None = None
    panel_index: int | None = Field(default=None, ge=1)


class StoryboardLayout(BaseModel):
    panel_count: int = Field(gt=0)
    rows: int | None = Field(default=None, gt=0)
    columns: int | None = Field(default=None, gt=0)
    reading_order: Literal["left_to_right", "top_to_bottom", "right_to_left", "bottom_to_top"] = (
        "left_to_right"
    )


class CheckItem(BaseModel):
    id: str
    question: str
    expected: str = "yes"
    evidence_type: str = "visual_semantic"
    required_evidence: list[str] = Field(default_factory=list)
    action: ActionSpec | None = None
    depends_on: list[str] = Field(default_factory=list)


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
    storyboard: StoryboardLayout | None = None


class JudgeCheckResult(BaseModel):
    id: str
    question: str = ""
    score: float = Field(ge=0, le=1)
    reason: str = ""
    evidence: list[str] = Field(default_factory=list)


class EditScore(BaseModel):
    sc: float | None = Field(default=None, ge=0, le=10)
    e_pq: float | None = Field(default=None, ge=0, le=10)
    edit_success: float | None = Field(default=None, ge=0, le=10)
    overedit_control: float | None = Field(default=None, ge=0, le=10)
    naturalness: float | None = Field(default=None, ge=0, le=10)
    artifact_free: float | None = Field(default=None, ge=0, le=10)

    def derive(self) -> EditScore:
        if self.edit_success is not None and self.overedit_control is not None:
            self.sc = min(self.edit_success, self.overedit_control)
        if self.naturalness is not None and self.artifact_free is not None:
            self.e_pq = min(self.naturalness, self.artifact_free)
        return self

    @model_validator(mode="after")
    def derive_sc_pq(self) -> EditScore:
        return self.derive()


class ReferenceScore(BaseModel):
    cp: float = Field(ge=0, le=4)
    pf: float = Field(ge=0, le=4)


class JudgeResult(BaseModel):
    task_score: float = Field(ge=0, le=1)
    text_layout_score: float | None = Field(default=None, ge=0, le=1)
    g_pq: float = Field(ge=0, le=10)
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
