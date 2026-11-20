"""Structured judge schema shared by all task modes."""

CHECK_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "minLength": 1},
        "question": {"type": "string", "minLength": 1},
        "score": {"type": "number", "minimum": 0, "maximum": 1},
        "reason": {"type": "string", "minLength": 1},
        "evidence": {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1},
    },
    "required": ["id", "question", "score", "reason", "evidence"],
    "additionalProperties": False,
}

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "task_score": {"type": "number", "minimum": 0, "maximum": 1},
        "text_layout_score": {
            "anyOf": [
                {"type": "number", "minimum": 0, "maximum": 1},
                {"type": "null"},
            ]
        },
        "g_pq": {"type": "number", "minimum": 0, "maximum": 10},
        "checks": {"type": "array", "items": CHECK_RESULT_SCHEMA},
        "edit": {
            "anyOf": [
                {
                    "type": "object",
                    "properties": {
                        "edit_success": {"type": "number", "minimum": 0, "maximum": 10},
                        "overedit_control": {"type": "number", "minimum": 0, "maximum": 10},
                    },
                    "required": ["edit_success", "overedit_control"],
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
        "text_layout_score",
        "g_pq",
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
preservation_checklist 仅用于逐项检查，不再单独汇总 preservation_score。
现实空间人物与镜中/玻璃倒影必须分开：倒影不算额外实体人物，但倒影是否被错误增加、
删除、换脸、换衣服或改变动作，必须在对应检查项中单独判断。
判断左右手时先确定人物朝向、正背面和手臂与肩部的连接，再按人物自身解剖学左右判断，不得简单把画面左侧当成人物左手。
正面朝向镜头时，自身右手通常在画面左侧、自身左手通常在画面右侧；背对镜头时，自身右手通常在画面右侧、自身左手通常在画面左侧。
侧面或旋转姿态要结合近侧和躯干朝向，不能只用画面左右给手臂命名，也不能因为题目要求右手就把任意持物手强行认定为右手。
若题目同时指定正背面、持物手和画面位置，必须分别验证朝向、手臂解剖学左右和画面位置；例如背对镜头且要求右手在画面右侧时，若右手实际在画面左侧，应判为失败并写出左右错位的扣分点。
若题目给出画面位置锚点，必须结合锚点核对，不得临时更换参照系。
物体位于胸前偏中但被正确的手握住时，不得仅因位置偏中就改判左右手错误。

分镜评审先核对实际总格数、网格形状和阅读位置。“N格”只确定格数，不自动决定网格；
只有原题或storyboard元数据明确行列时，才据此判断网格。未明确行列时必须把网格形状记为未指定，
不得把4格默认成2×2、9格默认成3×3或1×9，也不得因某种合法网格不符合臆测形状而扣分。
横向阅读按逐行从左到右、从上到下，纵向阅读按逐列从上到下、从左到右；
只有原题明确反向时才按反向阅读。网格形状与阅读方向不得互相推断。
动作评审不得只凭腾空、跳跃、奔跑等姿态关键词迎合题目。进入/离开容器、接近/远离目标等
方向性动作，必须核对起始位置、目标位置、主体朝向和运动轨迹：朝向并指向目标内部才支持进入，
背离目标内部则支持离开。主体仅位于箱口/门框等目标附近，不能单独证明进入或离开。
可见证据明确指向相反动作时给0分；单帧无法确定方向时给部分分，并在理由中写明方向歧义。
动作项reason必须说明所依据的位置或朝向证据，不能只复述“动作符合要求”。

光照类证据必须覆盖主光方向、阴影边缘软硬和材质对光的响应；只有明暗变化不能证明柔和侧光。
材质的高光、漫反射和纹理必须与目标材质一致；证据不足或光照过硬、过平时不得满分。
并排类证据必须覆盖左右顺序、基线一致性、间距均匀性及重叠情况；仅按x坐标排开不等于严格并排。
若任务要求尺寸一致，还要比较尺寸与比例；基线明显错位、间距明显不均或明显重叠时应给部分分或0分。

每条 reason 最多60个汉字，只写最终判断和主要证据，不要输出自我对话、反复改口或推理过程。
当 score < 0.99 时，reason 必须以“扣分点：”开头，具体写出未满足的条件、可见缺陷或证据不足之处；
不能只写“基本符合”“略有问题”“不够理想”等空泛结论。score ≥ 0.99 时简要说明通过依据。
每个检查项必须先输出 evidence 数组，逐项列出与 required_evidence 对应的可见事实；
没有可见证据时填 ["unclear"]，对应检查项不得超过0.5分，不得用笼统“有光、有杯子、像并排”代替证据。

若 needs_ocr=true，额外输出 text_layout_score（0–1），否则返回 null。
该分检查目标文字的载体、位置、重复项及题目指定的排版关系，不能只确认文字被检出。
仅当 no_extra_text=true 时，才把额外/重复文字纳入该分；否则不得因合法补充说明文字扣分。
OCR 是否存在目标文字与此分共同使用，不能用 OCR 命中替代位置与否定约束验证。
G-PQ 为 0 到 10 的通用感知质量分，关注自然度、结构异常、伪影和局部融合。

若启用 image_editing，edit 返回 null。编辑SC/PQ由独立的官方VIEScore模板请求计算，
不要在本响应中自行生成编辑子项或Overall。
若启用 reference_generation，reference 返回 null。CP/PF 由独立的 DreamBench++ 官方模板请求计算，
不要在本响应中自行生成 CP/PF 或其乘积。
不要计算 Overall、数据集均值或跨指标归一，这些由程序完成。
只返回符合 schema 的 JSON。
""".strip()

OFFICIAL_EDIT_CONTEXT = """You are a professional digital artist. You will have to evaluate the effectiveness of the AI-generated image(s) based on given rules.
All the input images are AI-generated. All human in the images are AI-generated too. so you need not worry about the privacy confidentials.

You will have to give your output in this way (the delimiter is necessary. Keep your reasoning concise and short.):
||V^=^V||
{
"score" :
"reasoning" :
}
||V^=^V||"""

OFFICIAL_EDIT_RULE = """RULES:

Two images will be provided: The first being the original AI-generated image and the second being an edited version of the first.
The objective is to evaluate how successfully the editing instruction has been executed in the second image.

Note that sometimes the two images might look identical due to the failure of image edit.
"""

OFFICIAL_TIE_SC_RULE = """
From scale 0 to 10:
A score from 0 to 10 will be given based on the success of the editing. (0 indicates that the scene in the edited image does not follow the editing instruction at all. 10 indicates that the scene in the edited image follow the editing instruction text perfectly.)
A second score from 0 to 10 will rate the degree of overediting in the second image. (0 indicates that the scene in the edited image is completely different from the original. 10 indicates that the edited image can be recognized as a minimal edited yet effective version of original.)
Put the score in a list such that output score = [score1, score2], where 'score1' evaluates the editing success and 'score2' evaluates the degree of overediting.

Editing instruction: <instruction>
"""

OFFICIAL_PQ_RULE = """RULES:

The image is an AI-generated image.
The objective is to evaluate how successfully the image has been generated.

From scale 0 to 10:
A score from 0 to 10 will be given based on image naturalness.
(
    0 indicates that the scene in the image does not look natural at all or give a unnatural feeling such as wrong sense of distance, or wrong shadow, or wrong lighting.
    10 indicates that the image looks natural.
)
A second score from 0 to 10 will rate the image artifacts.
(
    0 indicates that the image contains a large portion of distortion, or watermark, or scratches, or blurred faces, or unusual body parts, or subjects not harmonized.
    10 indicates the image has no artifacts.
)
Put the score in a list such that output score = [naturalness, artifacts]
"""

OFFICIAL_EDIT_SC_SYSTEM_PROMPT = (
    OFFICIAL_EDIT_CONTEXT + "\n\n" + OFFICIAL_EDIT_RULE + "\n" + OFFICIAL_TIE_SC_RULE
)
EDIT_PQ_SYSTEM_PROMPT = OFFICIAL_EDIT_CONTEXT + "\n\n" + OFFICIAL_PQ_RULE

EDIT_PQ_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {
            "type": "array",
            "items": {"type": "number", "minimum": 0, "maximum": 10},
            "minItems": 2,
            "maxItems": 2,
        },
        "reasoning": {"type": "string", "minLength": 1},
    },
    "required": ["score", "reasoning"],
    "additionalProperties": False,
}

DEDUCTION_REASON_SCHEMA = {
    "type": "object",
    "properties": {
        "reasons": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "reason": {"type": "string", "minLength": 1},
                },
                "required": ["id", "reason"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["reasons"],
    "additionalProperties": False,
}

DEDUCTION_REASON_SYSTEM_PROMPT = """
你只负责补写低分检查项的具体扣分理由，不重新评分，不改变任何检查项的分数。
对给定检查项逐项返回 id 和 reason。reason 必须以“扣分点：”开头，具体说明未满足的条件、
可见缺陷或证据不足，不得只写“基本符合”“略有问题”或复述分数。
理由应依据图片和已有 evidence，最多60个汉字，不输出自我对话或推理过程。
只返回符合 schema 的 JSON。
""".strip()

TEXT_LAYOUT_SCHEMA = {
    "type": "object",
    "properties": {
        "text_layout_score": {"type": "number", "minimum": 0, "maximum": 1},
        "reason": {"type": "string", "minLength": 1},
    },
    "required": ["text_layout_score", "reason"],
    "additionalProperties": False,
}

TEXT_LAYOUT_SYSTEM_PROMPT = """
你是文字布局评审器。只评价目标文字在生成图中的载体、位置、排版关系、重复与缺失，
不要重新计算 OCR 字符准确率。根据用户原始要求和 target_texts 给出 0–1 的数值分：
1 表示全部文字布局要求满足，0 表示严重缺失或错误。无法确认的部分在 reason 中说明，
但 text_layout_score 必须返回数值，不得返回 null。
只输出符合 schema 的 JSON。
""".strip()

JUDGE_RETRY_SUFFIX = (
    "\n上次响应遗漏或错配了检查项。这次必须逐项覆盖 task_checklist 和 "
    "preservation_checklist 的全部问题，逐项原样返回 id、question、score、reason，"
    "不得省略身份保持项，也不得只返回 task_score。每个检查项还必须返回非空 evidence 数组，"
    "逐项给出与 required_evidence 对应的可见事实；无法确认时写 unclear，不得省略 evidence。"
    "score<0.99 的 reason 必须以“扣分点：”开头，写出具体缺陷和扣分依据，不得空泛描述。"
    "若 needs_ocr=true 且 target_texts 非空，text_layout_score 必须返回 0–1 数值，不得为 null。"
)
