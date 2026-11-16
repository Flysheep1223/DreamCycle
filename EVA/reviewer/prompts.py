"""Separate schemas and prompts for evaluation audit and independent prompt advice."""

from EVA.router.prompts import CHECK_ITEM_SCHEMA

EVALUATION_AUDIT_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_assessment": {"type": "string"},
        "evaluation_prompt_suggestions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "additional_checks": {"type": "array", "items": CHECK_ITEM_SCHEMA},
        "possible_judge_errors": {
            "type": "array",
            "items": {"type": "string"},
        },
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": [
        "overall_assessment",
        "evaluation_prompt_suggestions",
        "additional_checks",
        "possible_judge_errors",
        "confidence",
    ],
    "additionalProperties": False,
}

PROMPT_SUGGESTION_SCHEMA = {
    "type": "object",
    "properties": {
        "generation_prompt_suggestions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "revised_generation_prompt": {"type": "string"},
    },
    "required": ["generation_prompt_suggestions", "revised_generation_prompt"],
    "additionalProperties": False,
}

EVALUATION_AUDIT_PROMPT = """
你是独立的评测流程审计器，不是给分器，也不能修改现有分数。
你会看到原始 Prompt、全部输入图、生成图、路由、逐项评分与理由、OCR、
各分离指标的原始尺度，以及全项通过率。必须审查图像效果和评分是否可靠。

任务：
1. overall_assessment 概括最重要的图像缺陷与评估问题，避免只说“提升质量”。
2. evaluation_prompt_suggestions 指出路由/评审提示词如何改进，是否应增加数量、
   遮挡、否定、文字、身份、保持或对照检查。
3. additional_checks 给出目前遗漏但可看图验证的新检查项，使用不与现有项重复的 ID。
4. possible_judge_errors 指出评分与图像证据可能不一致、评分过宽、漏评或问题歧义；
   如果未发现则返回空数组，不得为了显得严格而编造错误。
5. confidence 表示你对本次审计的把握。只返回符合 schema 的 JSON。
""".strip()

PROMPT_SUGGESTION_PROMPT = """
你是独立的生图 Prompt 改写助手。你只能看到用户原始需求、当前草稿和相关图像，
看不到任何已有评分、评审理由或评估争议。不得猜测或回应这些评估，
也不要根据某个分数判断应该如何降低任务难度。

改写目标是减少歧义，而不是持续累加约束：
1. 用户原始需求是唯一的任务事实来源和不可变锚点；当前草稿只是待修改措辞。
   保留原始全部约束，但不得把草稿新增的物体、数量、材质、位置或禁令自动当成用户要求。
   只能重述、压缩或消除原句歧义，不得新增任何可检查条件，包括但不限于物体属性、
   颜色、数量、位置、视角、正背面关系、材质、结构、字体、阴影、背景细节和风格限制。
   若原句没有规定某项，就继续保持未规定；把可选创意留在建议中，不写入最终 Prompt。
2. 当前草稿是历史最佳检查点，不是随意丢弃的上一步。先对照最佳图像识别其中已经满足
   原始要求的部分：对应的有效 Prompt 句子、语序和关键搭配应尽量原样继承，不得为了精简
   或追求每轮不同而重写这些有效部分。每轮只修改最多两个仍有歧义的已有要求。
   已经清楚的表达保持不变，
   不要复述同一要求，不要叠加“严格、绝对、完全、100%”等强调词。
3. 优先用正向、可见的目标状态表达。不得因为图中出现某个多余物体，就把该物体名称
   新写进禁令；原始需求已有的关键否定可以保留一次。不要新增原需求没有的细碎限制。
4. generation_prompt_suggestions 只列本轮实际做出的少量修改。
   revised_generation_prompt 必须简洁、完整、可直接生图，并遵守输入中的字符预算。
5. 文字任务中，每段目标文字只写一次，保留准确字符，不额外设计字体、装饰或其他文字。
6. 编辑任务只描述目标修改和一条整体保持要求；不得逐项编造源图的物体数量、颜色、位置、
   光照或材质。保持事实只能依据输入原图，不能把生成图中的新细节写成必须保留的要求。
7. 如果原始 Prompt 与输入图像事实明显矛盾，指出该前提问题；不得通过看图臆造源图事实。
8. 如果无法在不新增条件的情况下改善，直接返回当前最佳草稿，不要重置掉已经继承的有效表达。
只返回符合 schema 的 JSON。
""".strip()
