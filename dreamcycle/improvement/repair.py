"""Single-failure repair advice and deterministic repair-base selection."""

from __future__ import annotations

import json

from dreamcycle.ark import ArkClient
from dreamcycle.dream_indicators.selection import compare_to_incumbent, select_pareto_candidate
from dreamcycle.improvement.prompts import SIMPLE_REVISION_SCHEMA
from dreamcycle.io.images import image_part, text_part
from dreamcycle.schemas import AdviceReport, EvaluationResult, RouteDecision

REPAIR_SCHEMA = {
    **SIMPLE_REVISION_SCHEMA,
    "properties": {
        **SIMPLE_REVISION_SCHEMA["properties"],
        "target_check_ids": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "uniqueItems": True,
        },
    },
    "required": [*SIMPLE_REVISION_SCHEMA["required"], "target_check_ids"],
}

REPAIR_SYSTEM_PROMPT = """
你是联合定向图片修复顾问。你会看到原始 A、当前修复基图、同一原始检查清单、
两边逐项评分及当前基图相对原始 A 的指标变化。你的任务是把当前所有可修失败项
一次列入同一条图片编辑指令，同时保留已经满足和改善的部分。

规则：
1. 原始用户需求不可降低。target_check_ids 必须覆盖当前所有可看图修复的失败检查项，
   ID必须从现有检查项中原样选择，不得遗漏可修失败，也不得加入已通过项。
2. 每轮联合修复当前全部可修问题：优先处理相对原始 A 新增的退化，同时处理原始 A
   已存在且当前仍未满足的要求。将相关修改组织成一条连贯指令，避免重复描述或互相冲突。
3. 必须保留当前基图相对原始 A 已经改善的内容，以及其他已通过项。编辑指令要明确
   “一起修改哪些失败项”和“其余保持”，不要把基图中的偶然细节逐项编造成用户原始要求。
4. 使用正向、可见的目标状态，避免连续堆叠否定词。不得改变原始目标文字、数量、
   身份或布局要求，不得通过降低标准来制造改善。
5. 分镜修复必须区分总格数、网格和阅读顺序；N格不自动等于任何网格，只有原题明确
   M×N或行列时才确定形状。横向按行从左到右、从上到下，纵向按列从上到下、从左到右，
   不得把4格默认成2×2、9格默认成3×3或1×9。进入/离开等方向性动作
   必须明确主体从哪里到哪里、头与前肢朝向及目标容器，不得只用腾空姿态代替动作方向。
6. 若需求包含正/背面与左右手持物，修复时必须同时说明人物朝向、持物手自身左右和画面位置：
   正面时自身右手通常在画面左侧，背对镜头时自身右手通常在画面右侧；
   不得只因当前图片左右相反就改判题目要求，也不得把另一只手误写成目标手。
7. revised_generation_prompt 必须是可直接用于“以当前基图为输入图”的编辑指令，
   不是从零重写的原始 Prompt。overall_assessment 说明当前最重要的可修问题；
   generation_prompt_suggestions 说明目标检查项和保持项。
8. 必须检查 original_a_ocr 和 current_base_ocr。若目标文字出现错字、漏字或 CER 上升，
   即使对应 VLM 文字检查满分，也要把相关文字检查 ID 加入 target_check_ids，
   并在编辑指令中明确准确文字与清晰排版。F1 中的额外 OCR 行只用于提示非目标文字；
   不得为了提高 F1 删除用户明确要求或画面合理存在的文字。
只返回符合 schema 的 JSON。
""".strip()


def check_change_counts(original: dict, candidate: dict) -> tuple[int, int]:
    before = {item["id"]: item["score"] for item in original.get("checks", [])}
    after = {item["id"]: item["score"] for item in candidate.get("checks", [])}
    common = before.keys() & after.keys()
    improved = sum(after[check_id] > before[check_id] for check_id in common)
    degraded = sum(after[check_id] < before[check_id] for check_id in common)
    return improved, degraded


def has_repair_potential(original: dict, candidate: dict) -> bool:
    """Keep a base only when it preserves at least as many checks as it improves."""
    improved, degraded = check_change_counts(original, candidate)
    return improved > 0 and degraded <= improved


def all_requirements_pass(metrics: dict, threshold: float = 0.90) -> bool:
    checks = metrics.get("checks", [])
    return bool(checks) and all(item.get("score", 0) >= threshold for item in checks)


def strict_success(original: dict, candidate: dict) -> bool:
    """Pause successfully only for a full checklist pass without any protected regression."""
    return all_requirements_pass(candidate) and compare_to_incumbent(original, candidate)["accepted"]


def best_partial_candidate(original: dict, attempts: list[dict]) -> dict | None:
    """Keep the best no-regression improvement even when the full checklist is not complete."""
    selected, _ = select_pareto_candidate(original, attempts)
    return attempts[selected] if selected is not None else None


class TargetedRepairAdvisor:
    def __init__(self, client: ArkClient):
        self.client = client

    async def review(
        self,
        *,
        original_prompt: str,
        base_prompt: str,
        route: RouteDecision,
        original_a: EvaluationResult,
        base: EvaluationResult,
        original_input_images: list[str],
    ) -> tuple[AdviceReport, dict]:
        payload = {
            "original_user_prompt": original_prompt,
            "current_base_prompt": base_prompt,
            "route": route.model_dump(mode="json"),
            "original_a_checks": original_a.metrics.get("checks", []),
            "current_base_checks": base.metrics.get("checks", []),
            "original_a_ocr": original_a.metrics.get("ocr"),
            "current_base_ocr": base.metrics.get("ocr"),
            "comparison_to_original_a": compare_to_incumbent(
                original_a.metrics, base.metrics
            ),
            "note": "图片顺序：原始输入参考图、原始 A、当前修复基图。每轮一起修复当前全部可修失败项。",
        }
        content = [text_part(json.dumps(payload, ensure_ascii=False))]
        for index, path in enumerate(original_input_images):
            content.append(text_part(f"原始输入参考图 {index + 1}"))
            content.append(image_part(path, detail="high", max_side=1536))
        content.append(text_part("原始 A"))
        content.append(image_part(original_a.image.path, detail="high", max_side=1536))
        content.append(text_part("当前修复基图"))
        content.append(image_part(base.image.path, detail="high", max_side=1536))
        raw = await self.client.chat_json(
            system=REPAIR_SYSTEM_PROMPT,
            user_content=content,
            schema=REPAIR_SCHEMA,
            schema_name="single_failure_targeted_repair",
        )
        targets = raw["target_check_ids"]
        valid_ids = {item["id"] for item in base.metrics.get("checks", [])}
        unknown = [target for target in targets if target not in valid_ids]
        if unknown:
            correction = text_part(
                f"上一响应包含不存在的 target_check_ids：{unknown}。"
                f"只能从这些合法 ID 中选择：{sorted(valid_ids)}。"
                "请重新返回完整 JSON，覆盖当前全部可修失败项，不得创造新 ID。"
            )
            raw = await self.client.chat_json(
                system=REPAIR_SYSTEM_PROMPT,
                user_content=[*content, correction],
                schema=REPAIR_SCHEMA,
                schema_name="single_failure_targeted_repair",
            )
            targets = raw["target_check_ids"]
            unknown = [target for target in targets if target not in valid_ids]
            if unknown:
                raise ValueError(f"Repair advisor returned unknown target_check_ids: {unknown}")
        return AdviceReport.model_validate(raw), raw
