"""Deterministic route validation and low-confidence union rules."""

from __future__ import annotations

from EVA.schemas import CheckItem, RouteDecision, TaskMode


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value.strip() for value in values if value.strip()))


def normalize_route(
    route: RouteDecision,
    *,
    input_images: list[str],
    explicit_target_texts: list[str],
    prompt: str,
    low_confidence_threshold: float = 0.45,
    has_explicit_control: bool = False,
) -> RouteDecision:
    modes = list(dict.fromkeys(route.modes))
    if not input_images:
        modes = [TaskMode.TEXT_TO_IMAGE]
    elif route.confidence < low_confidence_threshold:
        ambiguous = (TaskMode.IMAGE_EDITING, TaskMode.REFERENCE_GENERATION)
        if modes and set(modes).issubset(ambiguous):
            modes = list(dict.fromkeys([*modes, *ambiguous]))
    if not modes:
        modes = [TaskMode.TEXT_TO_IMAGE]

    targets = _dedupe([*route.target_texts, *explicit_target_texts])
    task_checks = route.task_checklist or [
        CheckItem(
            id="task_full_prompt", question=f"生成图是否满足原始要求：{prompt}", expected="yes"
        )
    ]
    preservation_checks = route.preservation_checklist
    if input_images and not preservation_checks:
        preservation_checks = [
            CheckItem(
                id="preserve_unrequested_content",
                question="指令未要求改变的输入图内容是否得到保持？",
                expected="yes",
            )
        ]

    return route.model_copy(
        update={
            "modes": modes,
            "needs_ocr": route.needs_ocr or bool(targets),
            "needs_control": route.needs_control and has_explicit_control,
            "multi_reference": route.multi_reference and len(input_images) >= 2,
            "target_texts": targets,
            "task_checklist": task_checks,
            "preservation_checklist": preservation_checks,
        }
    )
