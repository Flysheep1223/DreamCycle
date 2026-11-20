"""JSON schema and prompt for multi-label intent routing."""

ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "subject": {"type": "string"},
        "target": {"type": "string"},
        "expected_direction": {"type": "string", "enum": ["toward", "away"]},
        "panel_index": {"type": "integer", "minimum": 1},
        "region": {
            "anyOf": [
                {
                    "type": "object",
                    "properties": {
                        "x": {"type": "number", "minimum": 0, "maximum": 1},
                        "y": {"type": "number", "minimum": 0, "maximum": 1},
                        "width": {"type": "number", "exclusiveMinimum": 0, "maximum": 1},
                        "height": {"type": "number", "exclusiveMinimum": 0, "maximum": 1},
                    },
                    "required": ["x", "y", "width", "height"],
                    "additionalProperties": False,
                },
                {"type": "null"},
            ]
        },
    },
    "required": ["subject", "target", "expected_direction", "region"],
    "additionalProperties": False,
}

CHECK_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "question": {"type": "string"},
        "expected": {"type": "string"},
        "action": {"anyOf": [ACTION_SCHEMA, {"type": "null"}]},
        "depends_on": {"type": "array", "items": {"type": "string"}},
        "evidence_type": {
            "type": "string",
            "enum": [
                "lighting",
                "layout",
                "directional_action",
                "anatomical_side",
                "material",
                "identity",
                "text",
                "quality",
                "visual_semantic",
            ],
        },
        "required_evidence": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["id", "question", "expected"],
    "additionalProperties": False,
}

STORYBOARD_SCHEMA = {
    "type": "object",
    "properties": {
        "panel_count": {"type": "integer", "exclusiveMinimum": 0},
        "rows": {"anyOf": [{"type": "integer", "exclusiveMinimum": 0}, {"type": "null"}]},
        "columns": {"anyOf": [{"type": "integer", "exclusiveMinimum": 0}, {"type": "null"}]},
        "reading_order": {
            "type": "string",
            "enum": ["left_to_right", "top_to_bottom", "right_to_left", "bottom_to_top"],
        },
    },
    "required": ["panel_count", "rows", "columns", "reading_order"],
    "additionalProperties": False,
}

ROUTE_SCHEMA = {
    "type": "object",
    "properties": {
        "storyboard": {"anyOf": [STORYBOARD_SCHEMA, {"type": "null"}]},
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
同时设置 evidence_type 与 required_evidence：按光照、布局、方向动作、材质、身份、文字、画质和通用语义分类，
要求该类型最小可核验证据，而不是只写“有光、像并排、像同一主体”等结论词。

生成检查项时必须遵循：
- 区分现实空间实体与镜子/玻璃倒影，倒影不计为额外实体，但倒影内容要单独检查；
- 数量、位置、左右手、可见性与遮挡拆开，不用“元素大致存在”代替精确验证；
  左右手必须结合人物朝向与自身解剖左右，优先使用“人物自身左/右手＋画面位置锚点”；
- 光照与空间关系不能只写概括词：柔和侧光要分别检查主光方向、阴影边缘软硬、材质高光/漫反射；
  横排/并排要分别检查左右顺序、基线一致性、相邻间距和必要时的外观尺寸一致性；
  这些证据不明确时必须保留部分满足的可能，不能默认满分。
- 文字检查拆成内容、载体/位置、是否重复，以及明确禁止时的额外文字；
- 分镜任务必须把总格数、网格形状、行列数和阅读顺序拆开检查，并填写 storyboard 元数据。
  “N格”只确定panel_count，不自动决定rows/columns；只有用户明确写出M×N、行列数或具体布局时，
  才填写对应rows和columns。未明确网格时两者均为null，不得把4格默认成2×2、9格默认成3×3或1×9。
  横向阅读默认left_to_right（逐行从左到右、从上到下）；纵向阅读默认top_to_bottom
  （逐列从上到下、从左到右）。用户明确反向阅读时才使用right_to_left或bottom_to_top。
  网格形状与阅读方向不得互相推断。
- 动作检查必须写清起始状态、目标状态和空间参照。对进入/离开容器等动作，
  要检查主体相对目标的位置、头部/前肢朝向和运动轨迹；只有腾空姿态或位于目标附近，
  不足以证明正在进入或离开。单帧方向不明时允许部分满足并注明歧义，不得按预期剧情补齐证据。
- 对进入/离开、接近/远离等方向性动作，检查项必须同时填写 action 元数据：
  subject 写运动主体，target 写目标内部或目的地，expected_direction 按用户意图写 toward/away。
  分镜动作需给panel_index（从1开始，按reading_order计数）。若能明确分镜或局部区域，
  region 用归一化 x/y/width/height 标出；否则为null，由程序在网格明确时计算。
  例如3×3横向第5格为 {"x":0.333333,"y":0.333333,"width":0.333333,"height":0.333333}。
  未明确行列时不得编造region。非方向性检查项的 action 为 null。
  是否存在、坐/站/趴/睡姿、微笑、手持/佩戴、颜色、发芽、长苞、开花、落在某处静止等
  静态状态一律不得设置action；只有可见的运动方向或朝向目标的施力动作才可设置。
- depends_on 只用于“完整剧情、动作序列、阅读顺序是否依次正确”这类真正的顺序联合检查，
  列出对应子动作ID。不得给单格存在性、身份、颜色、材质、风格、独立位置等原子检查添加依赖；
  格子总数或布局错误应独立扣分，不得据此把其他独立优点全部清零。
  程序会限制顺序联合检查分数不得超过任何子项，不能用总述印象掩盖局部失败。
- 否定约束单列，例如不得换脸、不得改非目标招牌、不得新增人物或猫耳；
- 先对照源图事实。若用户要求保留/删除源图不存在的对象，或声称的数量与源图不符，
  写入 input_warnings，并生成源图事实检查项，不要把不可能要求当成普通生成失败。

no_extra_text 只在用户明确禁止其他文字、重复文字或要求全画面文字完全受控时为 true，
不能仅因为存在目标文字就设为 true。没有额外文字限制时，额外但合法的说明文字不应直接扣分。
只返回符合 schema 的 JSON。
""".strip()
