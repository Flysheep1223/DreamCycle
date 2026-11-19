"""One-call multimodal judge for generic, editing and reference criteria."""

from __future__ import annotations

import asyncio
import json
import re
from difflib import SequenceMatcher

from dreamcycle.ark import ArkClient
from dreamcycle.io.images import image_part, text_part
from dreamcycle.judge.dreambench_prompts import (
    OFFICIAL_CP_PLAN,
    OFFICIAL_CP_TASK,
    OFFICIAL_PF_PLAN,
    OFFICIAL_PF_TASK,
)
from dreamcycle.judge.errors import JudgeValidationError
from dreamcycle.judge.prompts import (
    EDIT_PQ_SCHEMA,
    EDIT_PQ_SYSTEM_PROMPT,
    JUDGE_RETRY_SUFFIX,
    JUDGE_SCHEMA,
    JUDGE_SYSTEM_PROMPT,
    OFFICIAL_EDIT_SC_SYSTEM_PROMPT,
    TEXT_LAYOUT_SCHEMA,
    TEXT_LAYOUT_SYSTEM_PROMPT,
)
from dreamcycle.schemas import (
    EditScore,
    JudgeCheckResult,
    JudgeResult,
    ReferenceScore,
    RouteDecision,
    TaskMode,
)


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
            "required_check_ids": [
                item.id for item in [*route.task_checklist, *route.preservation_checklist]
            ],
            "required_check_count": len(route.task_checklist)
            + len(route.preservation_checklist),
            "output_contract": (
                "checks必须逐项覆盖required_check_ids，数量必须等于required_check_count；"
                "不得只回答task_checklist，不得遗漏preservation_checklist。"
            ),
            "image_order": "先给全部输入图，最后一张是本次生成图。",
        }
        content = [text_part(json.dumps(instructions, ensure_ascii=False))]
        for index, path in enumerate(input_images):
            content.append(text_part(f"输入图 {index + 1}"))
            content.append(image_part(path, detail="high", max_side=1536))
        content.append(text_part("本次生成图"))
        content.append(image_part(generated_image, detail="high", max_side=1536))
        editing = TaskMode.IMAGE_EDITING in route.modes
        official_sc_system = OFFICIAL_EDIT_SC_SYSTEM_PROMPT.replace("<instruction>", prompt)
        official_sc_content = [text_part(official_sc_system)]
        for path in input_images:
            official_sc_content.append(image_part(path, detail="high", max_side=1536))
        official_sc_content.append(image_part(generated_image, detail="high", max_side=1536))
        edit_pq_content = [
            text_part(EDIT_PQ_SYSTEM_PROMPT),
            image_part(generated_image, detail="high", max_side=1536),
        ]
        reference_generation = TaskMode.REFERENCE_GENERATION in route.modes
        reference_cp_messages = [
            {"role": "user", "content": OFFICIAL_CP_TASK},
            {"role": "assistant", "content": OFFICIAL_CP_PLAN},
            {
                "role": "user",
                "content": [
                    *[image_part(path, detail="high", max_side=1536) for path in input_images],
                    image_part(generated_image, detail="high", max_side=1536),
                ],
            },
        ]
        reference_pf_messages = [
            {"role": "user", "content": OFFICIAL_PF_TASK},
            {"role": "assistant", "content": OFFICIAL_PF_PLAN},
            {
                "role": "user",
                "content": [
                    text_part(prompt),
                    image_part(generated_image, detail="high", max_side=1536),
                ],
            },
        ]
        attempts = []
        last_error = None
        for attempt in range(2):
            system = JUDGE_SYSTEM_PROMPT
            if attempt:
                system += JUDGE_RETRY_SUFFIX
            try:
                requests = [
                    self.client.chat_json(
                        system=system,
                        user_content=content,
                        schema=JUDGE_SCHEMA,
                        schema_name="seedream_judge",
                    )
                ]
                if editing:
                    requests.extend(
                        [
                            self.client.chat_json(
                                system=official_sc_system,
                                user_content=official_sc_content,
                                schema=EDIT_PQ_SCHEMA,
                                schema_name="official_edit_sc",
                            ),
                            self.client.chat_json(
                                system=EDIT_PQ_SYSTEM_PROMPT,
                                user_content=edit_pq_content,
                                schema=EDIT_PQ_SCHEMA,
                                schema_name="edit_perceptual_quality",
                            ),
                        ]
                    )
                if reference_generation:
                    requests.extend(
                        [
                            self._official_score_text(reference_cp_messages, metric="CP"),
                            self._official_score_text(reference_pf_messages, metric="PF"),
                        ]
                    )
                responses = await asyncio.gather(*requests)
                raw = responses[0]
                if editing:
                    official_sc_raw, edit_pq_raw = responses[1:3]
                if reference_generation:
                    reference_cp_raw, reference_pf_raw = responses[-2:]
            except (ValueError, TypeError) as exc:
                raw = {"error": f"{type(exc).__name__}: {exc}"}
                attempts.append(raw)
                last_error = exc
                continue
            attempts.append(raw)
            try:
                result = JudgeResult.model_validate(raw)
                result = self._reaggregate(route, result)
                if any(
                    item.required_evidence
                    for item in [*route.task_checklist, *route.preservation_checklist]
                ):
                    missing_evidence = [check.id for check in result.checks if not check.evidence]
                    if missing_evidence:
                        raise ValueError(f"VLM omitted required evidence: {missing_evidence}")
                if editing:
                    result.edit = EditScore(
                        edit_success=official_sc_raw["score"][0],
                        overedit_control=official_sc_raw["score"][1],
                        naturalness=edit_pq_raw["score"][0],
                        artifact_free=edit_pq_raw["score"][1],
                    )
                if TaskMode.IMAGE_EDITING in route.modes and result.edit is None:
                    raise ValueError("VLM omitted required edit scores")
                if editing and (result.edit.sc is None or result.edit.e_pq is None):
                    raise ValueError("VLM omitted required edit sub-scores")
                if reference_generation:
                    result.reference = ReferenceScore(
                        cp=self._parse_official_score(reference_cp_raw),
                        pf=self._parse_official_score(reference_pf_raw),
                    )
                if TaskMode.REFERENCE_GENERATION in route.modes and result.reference is None:
                    raise ValueError("VLM omitted required reference scores")
                if route.needs_ocr and route.target_texts and result.text_layout_score is None:
                    if attempt == 0:
                        raise ValueError("VLM omitted required text layout score")
                    layout_fallback = await self._text_layout_fallback(
                        route, prompt, generated_image
                    )
                    result.text_layout_score = float(layout_fallback["text_layout_score"])
                    raw["_text_layout_fallback"] = layout_fallback
                audit_raw = dict(raw)
                if editing:
                    audit_raw["_official_sc"] = official_sc_raw
                    audit_raw["_edit_pq"] = edit_pq_raw
                if reference_generation:
                    audit_raw["_official_cp"] = reference_cp_raw
                    audit_raw["_official_pf"] = reference_pf_raw
                audit_raw["_attempt"] = attempt + 1
                if attempt:
                    audit_raw["_previous_failed_attempts"] = attempts[:-1]
                return result, audit_raw
            except (ValueError, TypeError) as exc:
                last_error = exc
        raise JudgeValidationError(str(last_error), {"attempts": attempts})

    async def _text_layout_fallback(
        self, route: RouteDecision, prompt: str, generated_image: str
    ) -> dict:
        content = [
            text_part(
                json.dumps(
                    {
                        "original_prompt": prompt,
                        "target_texts": route.target_texts,
                        "no_extra_text": route.no_extra_text,
                    },
                    ensure_ascii=False,
                )
            ),
            image_part(generated_image, detail="high", max_side=1536),
        ]
        raw = await self.client.chat_json(
            system=TEXT_LAYOUT_SYSTEM_PROMPT,
            user_content=content,
            schema=TEXT_LAYOUT_SCHEMA,
            schema_name="text_layout_fallback",
        )
        score = float(raw["text_layout_score"])
        if not 0 <= score <= 1:
            raise ValueError("Text layout fallback returned an out-of-range score")
        return raw

    async def _official_score_text(self, messages: list[dict], *, metric: str) -> str:
        first = await self.client.chat_text(messages)
        try:
            self._parse_official_score(first)
            return first
        except ValueError:
            pass
        output_rule = (
            "Return exactly one line: Score: N"
            if metric == "CP"
            else "Return two lines: Analysis: <one concise sentence>; Score: N on the second line"
        )
        correction = (
            f"Your previous {metric} response did not include the required score. "
            "Do not debate task applicability or claim missing inputs. Evaluate only the provided "
            "generated image and text prompt; all images before the final generated image are "
            "reference inputs. Mentions of 图1/图2 in the prompt are user content, not a reason "
            f"to refuse scoring. Use an integer from 0 to 4. {output_rule}"
        )
        retry_messages = [
            *messages,
            {"role": "assistant", "content": first},
            {"role": "user", "content": correction},
        ]
        second = await self.client.chat_text(retry_messages)
        try:
            self._parse_official_score(second)
            return second
        except ValueError as exc:
            raise ValueError(
                f"Cannot parse DreamBench++ {metric} score after retry: {second[:300]}"
            ) from exc

    @staticmethod
    def _parse_official_score(content: str) -> float:
        matches = re.findall(
            r"(?im)^\s*score\s*:\s*([0-4](?:\.\d+)?)\s*(?:/\s*4)?\s*$", content
        )
        if not matches:
            raise ValueError(f"Cannot parse DreamBench++ score: {content[:300]}")
        return float(matches[-1])

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
                    evidence=match.evidence,
                )
            )
        task_count = len(route.task_checklist)
        task_scores = [check.score for check in canonical[:task_count]]
        update = {"checks": canonical}
        if not route.needs_ocr or not route.target_texts:
            update["text_layout_score"] = None
        if task_scores:
            update["task_score"] = sum(task_scores) / len(task_scores)
        return result.model_copy(update=update)
