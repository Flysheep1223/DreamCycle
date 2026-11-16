"""One-call multimodal judge for generic, editing and reference criteria."""

from __future__ import annotations

import json
from difflib import SequenceMatcher

from EVA.ark import ArkClient
from EVA.io.images import image_part, text_part
from EVA.judge.errors import JudgeValidationError
from EVA.judge.prompts import JUDGE_SCHEMA, JUDGE_SYSTEM_PROMPT
from EVA.schemas import JudgeCheckResult, JudgeResult, RouteDecision, TaskMode


class VLMJudge:
    def __init__(self, client: ArkClient):
        self.client = client

    async def evaluate(
        self,
        *,
        prompt: str,
        route: RouteDecision,
        input_images: list[str],
        generated_image: str,
    ) -> tuple[JudgeResult, dict]:
        instructions = {
            "original_prompt": prompt,
            "modes": [mode.value for mode in route.modes],
            "target_texts": route.target_texts,
            "no_extra_text": route.no_extra_text,
            "input_warnings": route.input_warnings,
            "task_checklist": [item.model_dump() for item in route.task_checklist],
            "preservation_checklist": [item.model_dump() for item in route.preservation_checklist],
            "image_order": "先给全部输入图，最后一张是本次生成图。",
        }
        content = [text_part(json.dumps(instructions, ensure_ascii=False))]
        for index, path in enumerate(input_images):
            content.append(text_part(f"输入图 {index + 1}"))
            content.append(image_part(path, detail="high", max_side=1536))
        content.append(text_part("本次生成图"))
        content.append(image_part(generated_image, detail="high", max_side=1536))
        attempts = []
        last_error = None
        for attempt in range(2):
            system = JUDGE_SYSTEM_PROMPT
            if attempt:
                system += (
                    "\n上次响应遗漏或错配了检查项。这次必须逐项覆盖 task_checklist 和 "
                    "preservation_checklist 的全部问题，逐项原样返回 id、question、score、reason，"
                    "不得省略身份保持项，也不得只返回 task_score。"
                )
            try:
                raw = await self.client.chat_json(
                    system=system,
                    user_content=content,
                    schema=JUDGE_SCHEMA,
                    schema_name="seedream_judge",
                )
            except (ValueError, TypeError) as exc:
                raw = {"error": f"{type(exc).__name__}: {exc}"}
                attempts.append(raw)
                last_error = exc
                continue
            attempts.append(raw)
            try:
                result = JudgeResult.model_validate(raw)
                result = self._reaggregate(route, result)
                if TaskMode.IMAGE_EDITING in route.modes and result.edit is None:
                    raise ValueError("VLM omitted required edit scores")
                if TaskMode.REFERENCE_GENERATION in route.modes and result.reference is None:
                    raise ValueError("VLM omitted required reference scores")
                audit_raw = dict(raw)
                audit_raw["_attempt"] = attempt + 1
                if attempt:
                    audit_raw["_previous_failed_attempts"] = attempts[:-1]
                return result, audit_raw
            except (ValueError, TypeError) as exc:
                last_error = exc
        raise JudgeValidationError(str(last_error), {"attempts": attempts})

    @staticmethod
    def _reaggregate(route: RouteDecision, result: JudgeResult) -> JudgeResult:
        """Match questions by text similarity, using IDs only as a small tie-breaker."""
        expected = [*route.task_checklist, *route.preservation_checklist]
        pairs = []
        for expected_index, item in enumerate(expected):
            expected_question = " ".join(item.question.split())
            for result_index, check in enumerate(result.checks):
                returned_question = " ".join(check.question.split())
                similarity = SequenceMatcher(None, expected_question, returned_question).ratio()
                if check.id == item.id:
                    similarity += 0.05
                pairs.append((-similarity, expected_index, result_index))
        pairs.sort()
        assignments = {}
        used_results = set()
        for negative_similarity, expected_index, result_index in pairs:
            similarity = -negative_similarity
            if similarity < 0.45:
                continue
            if expected_index in assignments or result_index in used_results:
                continue
            assignments[expected_index] = result.checks[result_index]
            used_results.add(result_index)
        missing = [item.id for index, item in enumerate(expected) if index not in assignments]
        if missing:
            raise ValueError(f"VLM returned missing or ambiguous checklist answers: {missing}")

        canonical = []
        for index, item in enumerate(expected):
            match = assignments[index]
            canonical.append(
                JudgeCheckResult(
                    id=item.id,
                    question=item.question,
                    score=match.score,
                    reason=match.reason,
                )
            )
        task_count = len(route.task_checklist)
        task_scores = [check.score for check in canonical[:task_count]]
        preservation_scores = [check.score for check in canonical[task_count:]]
        update = {"checks": canonical}
        if task_scores:
            update["task_score"] = sum(task_scores) / len(task_scores)
        if preservation_scores:
            update["preservation_score"] = sum(preservation_scores) / len(preservation_scores)
        return result.model_copy(update=update)
