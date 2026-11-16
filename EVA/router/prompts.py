"""JSON schema and prompt for multi-label intent routing."""

CHECK_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "question": {"type": "string"},
        "expected": {"type": "string"},
    },
    "required": ["id", "question", "expected"],
    "additionalProperties": False,
}

ROUTE_SCHEMA = {
    "type": "object",
    "properties": {
        "modes": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["text_to_image", "image_editing", "reference_generation"],
            },
            "minItems": 1,
            "uniqueItems": True,
        },
        "needs_ocr": {"type": "boolean"},
        "needs_control": {"type": "boolean"},
        "no_extra_text": {"type": "boolean"},
        "multi_reference": {"type": "boolean"},
        "input_warnings": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "reason": {"type": "string"},
        "target_texts": {"type": "array", "items": {"type": "string"}},
        "task_checklist": {"type": "array", "items": CHECK_ITEM_SCHEMA},
        "preservation_checklist": {"type": "array", "items": CHECK_ITEM_SCHEMA},
    },
    "required": [
        "modes",
        "needs_ocr",
        "needs_control",
        "no_extra_text",
        "multi_reference",
        "input_warnings",
        "confidence",
        "reason",
        "target_texts",
        "task_checklist",
        "preservation_checklist",
    ],
    "additionalProperties": False,
}

ROUTER_SYSTEM_PROMPT = """
你是图像生成效果评测的路由器，不负责给图像打分。
根据原始 Prompt、输入图片和输入角色，返回多标签任务路由与可验证检查项。

主任务可多选：
- text_to_image：纯文本生成；
- image_editing：修改已有源图；
- reference_generation：保持参考主体、身份或风格并生成新内容。
如果编辑和参考保持无法区分，同时返回两者，不要强行单选。

可叠加标签：needs_ocr、needs_control、multi_reference。
needs_control 只在存在姿态图、分割图、深度图、布局框等显式结构化控制条件时为 true；
普通的复杂构图、数量或位置要求不属于 needs_control。
target_texts 必须逐项提取用户要求准确渲染的原文，不要自行改写。
task_checklist 写应完成的条件，preservation_checklist 写应保持的条件。
每个检查项必须能由看图回答，expected 写期望答案，通常为 yes 或具体文字/数量。

生成检查项时必须遵循：
- 区分现实空间实体与镜子/玻璃倒影，倒影不计为额外实体，但倒影内容要单独检查；
- 数量、位置、左右手、可见性与遮挡拆开，不用“元素大致存在”代替精确验证；
  左右手必须结合人物朝向与自身解剖左右，优先使用“人物自身左/右手＋画面位置锚点”；
- 文字检查拆成内容、载体/位置、是否重复，以及明确禁止时的额外文字；
- 否定约束单列，例如不得换脸、不得改非目标招牌、不得新增人物或猫耳；
- 先对照源图事实。若用户要求保留/删除源图不存在的对象，或声称的数量与源图不符，
  写入 input_warnings，并生成源图事实检查项，不要把不可能要求当成普通生成失败。

no_extra_text 只在用户明确禁止其他文字、重复文字或要求全画面文字完全受控时为 true，
不能仅因为存在目标文字就设为 true。没有额外文字限制时，额外但合法的说明文字不应直接扣分。
只返回符合 schema 的 JSON。
""".strip()
