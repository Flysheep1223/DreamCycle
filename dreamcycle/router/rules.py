"""Deterministic route validation and low-confidence union rules."""

from __future__ import annotations

import re

from dreamcycle.schemas import CheckItem, RouteDecision, StoryboardLayout, TaskMode


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value.strip() for value in values if value.strip()))


def _is_sequence_joint(item: CheckItem) -> bool:
    text = f"{item.id} {item.question}".lower()
    return any(
        keyword in text
        for keyword in ("阅读顺序", "完整剧情", "动作序列", "依次", "reading_order", "sequence")
    )


def _limit_dependencies(checks: list[CheckItem]) -> list[CheckItem]:
    for item in checks:
        if item.depends_on and not _is_sequence_joint(item):
            item.depends_on = []
    return checks


DIRECTION_KEYWORDS = (
    "跳",
    "跃",
    "进入",
    "离开",
    "靠近",
    "远离",
    "走向",
    "飞往",
    "飞向",
    "跑向",
    "奔向",
    "爬进",
    "爬出",
    "移动到",
    "移向",
    "推向",
    "拉向",
    "扔向",
    "抛向",
    "送向",
    "滚向",
    "冲向",
    "挖",
    "浇水",
    "洒水",
    "放入",
    "放进",
    "投进",
    "倒进",
    "搬运",
    "取出",
    "拿出",
    "取回",
    "前进",
    "后退",
    "倒退",
    "jump",
    "walk",
    "enter",
    "exit",
    "approach",
    "leave",
    "move",
    "fly",
    "run",
    "dig",
    "water",
    "put",
    "throw",
    "push",
    "pull",
)


def _limit_action_metadata(checks: list[CheckItem]) -> list[CheckItem]:
    for item in checks:
        if item.action is None:
            continue
        text = f"{item.id} {item.question}".lower()
        if not any(keyword in text for keyword in DIRECTION_KEYWORDS):
            item.action = None
    return checks


PANEL_NUMBERS = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}


def _panel_index(item: CheckItem) -> int | None:
    match = re.search(r"第([一二三四五六七八九十\d]+)格", item.question)
    if match:
        return PANEL_NUMBERS.get(match.group(1)) or int(match.group(1))
    match = re.search(r"(?:panel|p)(\d+)(?:_|$)", item.id, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def _infer_origin(question: str) -> str | None:
    match = re.search(
        r"(?:从|自)([一-龥A-Za-z0-9_]+?)(?:里|内|中)?(?:跃出|跳出|离开|飞出|爬出|移出)",
        question,
    )
    if not match:
        return None
    origin = match.group(1)
    return origin if origin.endswith("内部") else f"{origin}内部"


def _infer_storyboard(prompt: str) -> StoryboardLayout | None:
    if "分镜" not in prompt:
        return None
    match = re.search(r"(\d+)\s*行\s*(\d+)\s*列", prompt)
    if not match:
        match = re.search(r"(\d+)\s*[×xX*]\s*(\d+)", prompt)
    if not match:
        return None
    rows, columns = int(match.group(1)), int(match.group(2))
    count_match = re.search(r"(\d+)\s*格", prompt)
    panel_count = int(count_match.group(1)) if count_match else rows * columns
    if rows * columns != panel_count:
        return None
    reading_order = (
        "top_to_bottom" if "纵向" in prompt or "按列" in prompt else "left_to_right"
    )
    return StoryboardLayout(
        panel_count=panel_count,
        rows=rows,
        columns=columns,
        reading_order=reading_order,
    )


EVIDENCE_REQUIREMENTS = {
    "lighting": ["light_direction", "shadow_softness", "material_response"],
    "layout": ["x_order", "baseline_alignment", "spacing_uniformity", "overlap"],
    "directional_action": ["start_location", "target_location", "heading", "trajectory"],
    "anatomical_side": ["body_facing", "shoulder_side", "handedness", "image_side", "held_object"],
    "material": ["specular_pattern", "diffuse_pattern", "texture"],
    "identity": ["identity_features", "consistency"],
    "text": ["content", "carrier", "position", "duplicates"],
    "quality": ["naturalness", "artifacts"],
    "visual_semantic": ["visible_evidence"],
}


def _infer_evidence_type(item: CheckItem) -> str:
    if item.action is not None:
        return "directional_action"
    text = f"{item.id} {item.question}".lower()
    if any(word in text for word in ("左手", "右手", "自身左", "自身右", "背对", "面对", "解剖学")):
        return "anatomical_side"
    if any(word in text for word in ("光照", "光线", "阴影", "侧光", "逆光", "背光", "自然光", "高光", "反射")):
        return "lighting"
    if any(word in text for word in ("材质", "丝绸", "棉布", "金属", "玻璃", "纹理", "高光", "漫反射")):
        return "material"
    if any(word in text for word in ("横排", "并排", "网格", "分镜", "间距", "基线", "排列", "布局", "位置关系", "比例")):
        return "layout"
    if any(word in text for word in ("文字", "字母", "数字", "招牌", "标题", "ocr", "日期", "label")):
        return "text"
    if any(word in text for word in ("身份", "同一只", "同一个", "主体保持", "相似度", "参考图")):
        return "identity"
    if any(word in text for word in ("自然", "伪影", "瑕疵", "模糊", "失真", "变形", "质量")):
        return "quality"
    return "visual_semantic"


def _apply_evidence_protocol(checks: list[CheckItem]) -> list[CheckItem]:
    for item in checks:
        if item.evidence_type == "visual_semantic":
            item.evidence_type = _infer_evidence_type(item)
        if not item.required_evidence:
            item.required_evidence = EVIDENCE_REQUIREMENTS.get(
                item.evidence_type, EVIDENCE_REQUIREMENTS["visual_semantic"]
            )
    return checks


def _normalize_action_metadata(checks: list[CheckItem]) -> list[CheckItem]:
    for item in checks:
        if item.action is None:
            continue
        if item.action.panel_index is None:
            item.action.panel_index = _panel_index(item)
        if item.action.expected_direction == "away":
            origin = _infer_origin(item.question)
            if origin:
                item.action.target = origin
    return checks


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

    if (
        route.storyboard
        and route.storyboard.rows is not None
        and route.storyboard.columns is not None
        and route.storyboard.rows * route.storyboard.columns != route.storyboard.panel_count
    ):
        raise ValueError("Storyboard rows × columns must equal panel_count")

    storyboard = route.storyboard or _infer_storyboard(prompt)

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
            "task_checklist": _normalize_action_metadata(
                _limit_action_metadata(_apply_evidence_protocol(_limit_dependencies(task_checks)))
            ),
            "preservation_checklist": _normalize_action_metadata(
                _limit_action_metadata(_apply_evidence_protocol(_limit_dependencies(preservation_checks)))
            ),
            "storyboard": storyboard,
        }
    )
