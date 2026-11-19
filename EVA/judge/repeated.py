"""Aggregate independent VLM evaluations field by field using deterministic modes."""

from __future__ import annotations

import asyncio
from collections import Counter
from typing import Any

from EVA.judge.judge import VLMJudge
from EVA.schemas import (
    EditScore,
    JudgeCheckResult,
    JudgeResult,
    ReferenceScore,
    RouteDecision,
)


def numeric_mode(values: list[float]) -> dict[str, Any]:
    """Return the mode; resolve equal-frequency numeric scores conservatively downward."""
    counts = Counter(values)
    highest = max(counts.values())
    leaders = [value for value, count in counts.items() if count == highest]
    selected = min(leaders)
    return {
        "selected": selected,
        "count": highest,
        "agreement": highest / len(values),
        "tied": len(leaders) > 1,
        "distribution": {str(value): count for value, count in sorted(counts.items())},
    }


def optional_numeric_mode(values: list[float | None]) -> dict[str, Any] | None:
    if all(value is None for value in values):
        return None
    if any(value is None for value in values):
        raise ValueError("VLM repeats disagree on whether a metric is applicable")
    return numeric_mode([value for value in values if value is not None])


class RepeatedVLMJudge:
    """Run N independent valid judge sessions and aggregate each model-scored field."""

    def __init__(self, judge: VLMJudge, *, repeats: int = 10):
        if repeats < 1:
            raise ValueError("repeats must be at least 1")
        self.judge = judge
        self.repeats = repeats

    async def evaluate(
        self,
        *,
        prompt: str,
        route: RouteDecision,
        input_images: list[str],
        generated_image: str,
    ) -> tuple[JudgeResult, dict]:
        async def one_run(index: int) -> tuple[JudgeResult, dict]:
            result, raw = await self.judge.evaluate(
                prompt=prompt,
                route=route,
                input_images=input_images,
                generated_image=generated_image,
            )
            return result, {**raw, "_repeat_index": index}

        # Any failed valid session fails the aggregation; failed runs are never silently dropped.
        runs = await asyncio.gather(
            *(one_run(index) for index in range(1, self.repeats + 1))
        )
        results = [item[0] for item in runs]
        raws = [item[1] for item in runs]
        first = results[0]
        checks = []
        check_stats = {}
        for position, expected in enumerate(first.checks):
            scores = [result.checks[position].score for result in results]
            stat = numeric_mode(scores)
            modal_score = stat["selected"]
            reasons = Counter(
                result.checks[position].reason
                for result in results
                if result.checks[position].score == modal_score
            )
            reason = min(
                reasons,
                key=lambda text: (-reasons[text], len(text), text),
            )
            evidence = next(
                (
                    result.checks[position].evidence
                    for result in results
                    if result.checks[position].score == modal_score
                    and result.checks[position].evidence
                ),
                ["unclear"],
            )
            checks.append(
                JudgeCheckResult(
                    id=expected.id,
                    question=expected.question,
                    score=modal_score,
                    reason=reason,
                    evidence=evidence,
                )
            )
            check_stats[expected.id] = stat

        field_stats = {
            "g_pq": numeric_mode([result.g_pq for result in results]),
            "text_layout_score": optional_numeric_mode(
                [result.text_layout_score for result in results]
            ),
        }
        edit = None
        if first.edit is not None:
            if first.edit.edit_success is not None:
                for field in (
                    "edit_success",
                    "overedit_control",
                    "naturalness",
                    "artifact_free",
                ):
                    field_stats[f"edit.{field}"] = numeric_mode(
                        [getattr(result.edit, field) for result in results if result.edit]
                    )
                edit = EditScore(
                    **{
                        field: field_stats[f"edit.{field}"]["selected"]
                        for field in (
                            "edit_success",
                            "overedit_control",
                            "naturalness",
                            "artifact_free",
                        )
                    }
                )
            else:
                field_stats["edit.sc"] = numeric_mode(
                    [result.edit.sc for result in results if result.edit]
                )
                field_stats["edit.e_pq"] = numeric_mode(
                    [result.edit.e_pq for result in results if result.edit]
                )
                edit = EditScore(
                    sc=field_stats["edit.sc"]["selected"],
                    e_pq=field_stats["edit.e_pq"]["selected"],
                )
        reference = None
        if first.reference is not None:
            field_stats["reference.cp"] = numeric_mode(
                [result.reference.cp for result in results if result.reference]
            )
            field_stats["reference.pf"] = numeric_mode(
                [result.reference.pf for result in results if result.reference]
            )
            reference = ReferenceScore(
                cp=field_stats["reference.cp"]["selected"],
                pf=field_stats["reference.pf"]["selected"],
            )

        tag_counts = Counter(tuple(sorted(result.failure_tags)) for result in results)
        highest_tag_count = max(tag_counts.values())
        failure_tags = list(
            min(tags for tags, count in tag_counts.items() if count == highest_tag_count)
        )
        aggregated = JudgeResult(
            task_score=first.task_score,
            text_layout_score=(
                field_stats["text_layout_score"]["selected"]
                if field_stats["text_layout_score"]
                else None
            ),
            g_pq=field_stats["g_pq"]["selected"],
            checks=checks,
            edit=edit,
            reference=reference,
            failure_tags=failure_tags,
        )
        # Recompute dependent means from modal checks; never take modes of the means independently.
        aggregated = VLMJudge._reaggregate(route, aggregated)
        numeric_stats = [stat for stat in field_stats.values() if stat is not None]
        numeric_stats.extend(check_stats.values())
        tied_fields = [
            *(check_id for check_id, stat in check_stats.items() if stat["tied"]),
            *(name for name, stat in field_stats.items() if stat and stat["tied"]),
        ]
        aggregation = {
            "strategy": "independent_field_mode",
            "runs": self.repeats,
            "successful_runs": len(results),
            "tie_break": "lower_numeric_score",
            "minimum_mode_agreement": min(stat["agreement"] for stat in numeric_stats),
            "tied_fields": tied_fields,
            "protocol_retries": sum(max(0, raw.get("_attempt", 1) - 1) for raw in raws),
            "checks": check_stats,
            "fields": field_stats,
            "failure_tags": {
                "selected": failure_tags,
                "count": highest_tag_count,
                "agreement": highest_tag_count / self.repeats,
            },
        }
        return aggregated, {
            "aggregation": aggregation,
            "attempts": raws,
            "aggregated_result": aggregated.model_dump(mode="json"),
        }
