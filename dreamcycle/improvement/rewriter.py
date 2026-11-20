"""Revise a prompt directly from A's failed checks, reasons, OCR evidence and image."""

from __future__ import annotations

import json

from dreamcycle.ark import ArkClient
from dreamcycle.improvement.prompts import SIMPLE_REVISION_PROMPT, SIMPLE_REVISION_SCHEMA
from dreamcycle.io.images import image_part, text_part
from dreamcycle.schemas import AdviceReport, EvaluationResult, RouteDecision


class FeedbackPromptRewriter:
    """Produce one evidence-guided revision; retry wording only if it returns a no-op."""

    def __init__(self, client: ArkClient):
        self.client = client

    async def revise(
        self,
        *,
        prompt: str,
        route: RouteDecision,
        result: EvaluationResult,
        input_images: list[str],
    ) -> tuple[AdviceReport, dict]:
        checks = result.metrics.get("checks", [])
        failed = [item for item in checks if item.get("score", 0) < 0.90]
        passed = [item for item in checks if item.get("score", 0) >= 0.90]
        payload = {
            "original_user_prompt": prompt,
            "failed_checks": failed,
            "passed_checks_to_preserve": [
                {"id": item.get("id"), "question": item.get("question")} for item in passed
            ],
            "failure_tags": result.failure_tags,
            "ocr_evidence": result.metrics.get("ocr"),
            "input_warnings": route.input_warnings,
            "note": "先给全部输入参考图，最后一张是待改进的 A 图片。请针对失败项实质修改 Prompt。",
        }
        content = [text_part(json.dumps(payload, ensure_ascii=False))]
        for index, path in enumerate(input_images):
            content.append(text_part(f"输入参考图 {index + 1}"))
            content.append(image_part(path, detail="high", max_side=1536))
        content.append(text_part("待改进的 A 图片"))
        content.append(image_part(result.image.path, detail="high", max_side=1536))

        raw = await self.client.chat_json(
            system=SIMPLE_REVISION_PROMPT,
            user_content=content,
            schema=SIMPLE_REVISION_SCHEMA,
            schema_name="single_ab_feedback_revision",
        )
        identical_retry = False
        if failed and raw["revised_generation_prompt"].strip() == prompt.strip():
            identical_retry = True
            correction = (
                "你返回了原始 Prompt，但仍存在未通过检查项。请逐条选择最值得修复的已有要求，"
                "对其数量、位置、绑定关系、文字载体或保持范围作实质澄清；不得只改标点或同义词。"
                "上一版回答：\n" + json.dumps(raw, ensure_ascii=False)
            )
            raw = await self.client.chat_json(
                system=SIMPLE_REVISION_PROMPT,
                user_content=[*content, text_part(correction)],
                schema=SIMPLE_REVISION_SCHEMA,
                schema_name="single_ab_feedback_revision_noop_correction",
            )
        report = AdviceReport.model_validate(raw)
        return report, {
            "prompt_suggestions": raw,
            "prompt_revision_policy": {
                "name": "single_ab_feedback_revision_v1",
                "failed_check_count": len(failed),
                "passed_check_count": len(passed),
                "identical_retry": identical_retry,
                "prompt_changed": report.revised_generation_prompt.strip() != prompt.strip(),
            },
        }
