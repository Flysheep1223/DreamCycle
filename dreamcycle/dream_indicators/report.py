"""Report separated metrics in their original units; never synthesize a total score."""

from __future__ import annotations

from typing import Any

from dreamcycle.schemas import (
    EvaluationResult,
    GeneratedImage,
    JudgeResult,
    OCRScore,
    RouteDecision,
)


class ScoreReporter:
    @staticmethod
    def report(
        *,
        image: GeneratedImage,
        route: RouteDecision,
        judge: JudgeResult,
        judge_raw: dict[str, Any],
        ocr: OCRScore | None,
    ) -> EvaluationResult:
        requirement_scores = [check.score for check in judge.checks]
        full_rate = (
            sum(score >= 0.99 for score in requirement_scores) / len(requirement_scores)
            if requirement_scores
            else None
        )
        minimum_requirement = min(requirement_scores) if requirement_scores else None
        edit = None
        if judge.edit:
            edit = {
                **judge.edit.model_dump(exclude_none=True),
                "overall": (judge.edit.sc * judge.edit.e_pq) ** 0.5,
            }
        aggregation = judge_raw.get("aggregation")
        aggregation_summary = None
        if aggregation:
            aggregation_summary = {
                key: aggregation[key]
                for key in (
                    "strategy",
                    "runs",
                    "successful_runs",
                    "tie_break",
                    "minimum_mode_agreement",
                    "tied_fields",
                    "protocol_retries",
                )
            }
        reference = None
        if judge.reference is not None:
            reference = {
                **judge.reference.model_dump(),
                "cppf": judge.reference.cp * judge.reference.pf,
            }
        metrics: dict[str, Any] = {
            "task_score": judge.task_score,
            "text_layout_score": judge.text_layout_score,
            "g_pq": judge.g_pq,
            "edit": edit,
            "reference": reference,
            "ocr": ocr.model_dump() if ocr else None,
            "checks": [check.model_dump() for check in judge.checks],
            "full_requirement_rate": full_rate,
            "minimum_requirement_score": minimum_requirement,
            "judge_aggregation": aggregation_summary,
        }
        return EvaluationResult(
            image=image,
            modes=route.modes,
            metrics=metrics,
            full_requirement_rate=full_rate,
            minimum_requirement_score=minimum_requirement,
            raw_scores={
                "judge": judge.model_dump(),
                "judge_raw": judge_raw,
                "ocr": ocr.model_dump() if ocr else None,
                "input_warnings": route.input_warnings,
                **({"edit": edit} if edit else {}),
                **({"reference": judge.reference.model_dump()} if judge.reference else {}),
            },
            failure_tags=judge.failure_tags,
        )
