"""Two-stage VLM audit: evaluation review followed by independent prompt advice."""

from __future__ import annotations

import json
import math

from EVA.ark import ArkClient
from EVA.io.images import image_part, text_part
from EVA.reviewer.prompts import (
    EVALUATION_AUDIT_PROMPT,
    EVALUATION_AUDIT_SCHEMA,
    PROMPT_SUGGESTION_PROMPT,
    PROMPT_SUGGESTION_SCHEMA,
)
from EVA.schemas import AdviceReport, EvaluationResult, RouteDecision


class PromptAdvisor:
    def __init__(self, client: ArkClient):
        self.client = client

    async def review(
        self,
        *,
        prompt: str,
        route: RouteDecision,
        result: EvaluationResult,
        input_images: list[str],
        original_prompt: str | None = None,
    ) -> tuple[AdviceReport, dict]:
        source_prompt = original_prompt or prompt
        prompt_character_budget = max(240, math.ceil(len(source_prompt) * 1.35))
        # Stage 1: audit both the image and the current evaluation, including all scores.
        audit_input = {
            "original_prompt": prompt,
            "route": route.model_dump(mode="json"),
            "scores_and_reasons": result.model_dump(mode="json"),
            "note": "后续先给全部输入图，最后一张是生成图。请同时审查图像和评分合理性。",
        }
        content = [text_part(json.dumps(audit_input, ensure_ascii=False))]
        for index, path in enumerate(input_images):
            content.append(text_part(f"输入图 {index + 1}"))
            content.append(image_part(path, detail="high", max_side=1536))
        content.append(text_part("生成图"))
        content.append(image_part(result.image.path, detail="high", max_side=1536))
        audit_raw = await self.client.chat_json(
            system=EVALUATION_AUDIT_PROMPT,
            user_content=content,
            schema=EVALUATION_AUDIT_SCHEMA,
            schema_name="evaluation_audit",
        )

        # Stage 2: never pass scores, judge reasons or disputed evaluations to prompt rewriting.
        suggestion_input = {
            "original_user_prompt": source_prompt,
            "current_draft_prompt": prompt,
            "checkpoint_role": "best_so_far",
            "prompt_character_budget": prompt_character_budget,
            "note": (
                "以original_user_prompt为不可变任务锚点。current_draft_prompt来自历史最佳检查点，"
                "必须继承其中已经有效的表达，只修改仍有歧义的已有要求；不要继承草稿新增要求，"
                "也不要新增任何可检查条件。若无法等义改善就返回当前最佳草稿，不要重置有效修改。"
                "最终Prompt不得超过字符预算。"
                "本次未提供任何评分、评审理由、OCR、评估意见或争议检查项；请独立看图判断。"
            ),
        }
        suggestion_content = [text_part(json.dumps(suggestion_input, ensure_ascii=False))]
        for index, path in enumerate(input_images):
            suggestion_content.append(text_part(f"输入图 {index + 1}"))
            suggestion_content.append(image_part(path, detail="high", max_side=1536))
        suggestion_content.append(text_part("当前草稿对应的生成图，不是新的任务事实来源"))
        suggestion_content.append(image_part(result.image.path, detail="high", max_side=1536))
        prompt_raw = await self.client.chat_json(
            system=PROMPT_SUGGESTION_PROMPT,
            user_content=suggestion_content,
            schema=PROMPT_SUGGESTION_SCHEMA,
            schema_name="independent_prompt_suggestions",
        )
        length_retry = False
        length_fallback = False
        if len(prompt_raw["revised_generation_prompt"]) > prompt_character_budget:
            length_retry = True
            correction = (
                f"上一版有{len(prompt_raw['revised_generation_prompt'])}个字符，超过"
                f"{prompt_character_budget}字符预算。请回到原始需求，只保留最多两处必要澄清，"
                "删除重复、强调词、新增禁令和对源图细节的逐项复述，重新返回完整JSON。上一版：\n"
                + prompt_raw["revised_generation_prompt"]
            )
            prompt_raw = await self.client.chat_json(
                system=PROMPT_SUGGESTION_PROMPT,
                user_content=[*suggestion_content, text_part(correction)],
                schema=PROMPT_SUGGESTION_SCHEMA,
                schema_name="independent_prompt_suggestions",
            )
        if len(prompt_raw["revised_generation_prompt"]) > prompt_character_budget:
            # Keep the best checkpoint rather than accepting bloat or losing effective edits.
            length_fallback = True
            prompt_raw["revised_generation_prompt"] = prompt
            prompt_raw["generation_prompt_suggestions"] = [
                "连续两次改写均超出字符预算，本轮保留历史最佳Prompt，避免约束膨胀或丢失有效修改。"
            ]
        report = AdviceReport.model_validate({**prompt_raw, **audit_raw})
        return report, {
            "evaluation_audit": audit_raw,
            "prompt_suggestions": prompt_raw,
            "prompt_revision_policy": {
                "name": "best_checkpoint_guarded_revision_v4",
                "original_prompt_characters": len(source_prompt),
                "current_prompt_characters": len(prompt),
                "revised_prompt_characters": len(report.revised_generation_prompt),
                "character_budget": prompt_character_budget,
                "length_retry": length_retry,
                "length_fallback": length_fallback,
            },
            "prompt_suggestion_excluded_context": [
                "task_score",
                "g_pq",
                "judge reasons",
                "OCR results",
                "evaluation audit opinions",
                "disputed checklist items",
            ],
        }
