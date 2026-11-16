"""Structured judge schema shared by all task modes."""

CHECK_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "question": {"type": "string"},
        "score": {"type": "number", "minimum": 0, "maximum": 1},
        "reason": {"type": "string"},
    },
    "required": ["id", "question", "score", "reason"],
    "additionalProperties": False,
}

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "task_score": {"type": "number", "minimum": 0, "maximum": 1},
        "preservation_score": {
            "anyOf": [
                {"type": "number", "minimum": 0, "maximum": 1},
                {"type": "null"},
            ]
        },
        "text_layout_score": {
            "anyOf": [
                {"type": "number", "minimum": 0, "maximum": 1},
                {"type": "null"},
            ]
        },
        "pq": {"type": "number", "minimum": 0, "maximum": 10},
        "checks": {"type": "array", "items": CHECK_RESULT_SCHEMA},
        "edit": {
            "anyOf": [
                {
                    "type": "object",
                    "properties": {
                        "sc": {"type": "number", "minimum": 0, "maximum": 10},
                        "pq": {"type": "number", "minimum": 0, "maximum": 10},
                    },
                    "required": ["sc", "pq"],
                    "additionalProperties": False,
                },
                {"type": "null"},
            ]
        },
        "reference": {
            "anyOf": [
                {
                    "type": "object",
                    "properties": {
                        "cp": {"type": "number", "minimum": 0, "maximum": 4},
                        "pf": {"type": "number", "minimum": 0, "maximum": 4},
                    },
                    "required": ["cp", "pf"],
                    "additionalProperties": False,
                },
                {"type": "null"},
            ]
        },
        "failure_tags": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "task_score",
        "preservation_score",
        "text_layout_score",
        "pq",
        "checks",
        "edit",
        "reference",
        "failure_tags",
    ],
    "additionalProperties": False,
}

JUDGE_SYSTEM_PROMPT = """
你是严格的图像生成效果评审器。只依据图像中可见证据评分，不推测生成模型名称。
按给定检查清单逐项输出 0 到 1 的分数，并给出简短扣分理由。
每个检查项必须原样返回输入的 id 和 question，不得重新编号、改写问题或错配答案。
检查项可以是部分满足，不必只有 0 或 1。task_score 表示任务完成度，
preservation_score 表示应保持内容的完成度；无保持要求时返回 null。
现实空间人物与镜中/玻璃倒影必须分开：倒影不算额外实体人物，但倒影是否被错误增加、
删除、换脸、换衣服或改变动作，必须在对应检查项中单独判断。
判断左右手时先确定人物朝向，再按人物自身解剖学左右判断，不得简单把画面左侧当成人物左手。
若题目给出画面位置锚点，必须结合锚点核对，不得临时更换参照系。
物体位于胸前偏中但被正确的手握住时，不得仅因位置偏中就改判左右手错误。

每条 reason 最多60个汉字，只写最终判断和主要证据，不要输出自我对话、反复改口或推理过程。

若 needs_ocr=true，额外输出 text_layout_score（0–1），否则返回 null。
该分检查目标文字的载体、位置、重复项及题目指定的排版关系，不能只确认文字被检出。
仅当 no_extra_text=true 时，才把额外/重复文字纳入该分；否则不得因合法补充说明文字扣分。
OCR 是否存在目标文字与此分共同使用，不能用 OCR 命中替代位置与否定约束验证。
PQ 为 0 到 10 的感知质量分，关注自然度、结构异常、伪影和局部融合。

若启用 image_editing，额外输出 edit.sc 和 edit.pq（0–10），否则 edit=null。
SC 同时考虑指定编辑是否完成和未要求变化的内容是否保持。
若启用 reference_generation，额外输出 reference.cp 和 reference.pf（0–4），
否则 reference=null。CP 只评参考概念/主体保持，PF 只评新 Prompt 遵循。
不要计算 Overall、数据集均值或跨指标归一，这些由程序完成。
只返回符合 schema 的 JSON。
""".strip()
