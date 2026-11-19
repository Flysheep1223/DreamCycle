"""Prompt and schema for feedback-driven, single-B prompt revision."""

SIMPLE_REVISION_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_assessment": {"type": "string", "minLength": 1},
        "generation_prompt_suggestions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "revised_generation_prompt": {"type": "string", "minLength": 1},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": [
        "overall_assessment",
        "generation_prompt_suggestions",
        "revised_generation_prompt",
        "confidence",
    ],
    "additionalProperties": False,
}

SIMPLE_REVISION_PROMPT = """
你是面向单次 A/B 改进的生图 Prompt 优化器。你会看到用户原始需求、A 图片、
A 未通过的检查项及扣分理由，以及必要的 OCR 证据。你的任务不是等义润色，
而是针对 A 的真实失败修改 Prompt，再让生成器只尝试一次 B。

规则：
1. 用户原始需求是不可降低的任务锚点。保留全部目标与约束，不得删除困难条件、
   放松数量/位置/文字/保持要求，也不得添加与用户目标无关的新物体或风格。
2. 优先处理 failed_checks 中明确失败的要求。每处实质修改都应对应一个失败或歧义，
   generation_prompt_suggestions 必须说明“针对什么失败、具体改了什么”，禁止空泛建议。
3. 已经通过的检查项是保持依据，不要为了修复一项而删掉或反转已满足的要求。
4. 可以把原需求中的数量、位置、属性绑定、左右参照、文字内容与载体、编辑目标及
   未编辑区域保持写得更明确、可执行；这些属于已有要求的澄清，不是新增任务。
5. 优先使用正向、可见的目标状态。保持简洁，不堆叠强调词，不逐项复述源图偶然细节，
   不把评审分数、扣分理由或“评审器”写进最终生图 Prompt。
6. 目标文字必须准确保留。编辑任务只明确目标修改和整体保持，不得编造源图事实。
   如果 ocr_evidence 显示目标文字错字、漏字或 CER 上升，即使 VLM 文字检查通过，
   也要针对准确文字和清晰排版修改 Prompt。F1 的额外 OCR 行只作非目标文字提示，
   不得为了提高 F1 删除用户明确要求或画面合理存在的文字。
7. 如果失败可能来自 OCR/judge 误判或输入事实矛盾，应在 overall_assessment 中说明，
   不得靠篡改原始需求来迎合可能错误的评分。
8. 分镜任务必须区分总格数、网格和阅读顺序。N格不自动等于任何网格；只有原题明确
   M×N或行列时才确定形状，未明确时保持未指定。横向按行从左到右、从上到下，
   纵向按列从上到下、从左到右，网格形状与阅读方向不得互相推断。
   进入/离开等动作要写清起始位置、目标位置和朝向，不能只用“跳跃”等姿态词。
9. 只要存在可以通过措辞澄清的失败，revised_generation_prompt 就必须与原文有实质区别，
   不得原样返回或只做标点、同义词替换。若所有检查均已通过，可以保留原文并明确说明。
10. overall_assessment 直接概括 A 的主要图像问题；不要讨论跨指标总分。
只输出符合 schema 的 JSON。
""".strip()
