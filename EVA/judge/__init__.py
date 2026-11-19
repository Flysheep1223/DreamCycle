r"""# judge 模块

基础 `VLMJudge` 一次 VLM 调用完成当前图片需要的评审；Pipeline 默认用 `RepeatedVLMJudge` 同时发起 10 个独立评审，再逐字段取众数：

- 动态检查项逐项给 0–1 分；
- 通用 G-PQ 给 0–10 分；
- `text_layout_score` 检查文字载体、位置、重复和指定排版关系；只有 `no_extra_text=true` 才评价额外文字；
- 现实人物与镜中倒影分开计数，但倒影内容是否被篡改单独判断；
- 编辑路由额外返回 SC/E-PQ；
- 参考图路由额外返回 CP/PF；
- 不适用的字段返回 `null`。

检查项均值由 `_reaggregate()` 在程序中重新计算，避免直接信任模型自报的平均分。每个回答必须同时回显 `id` 和 `question`，程序优先按问题相似度一对一匹配，ID 只作小幅辅助，允许合理改写但防止重排或错配；无法可靠匹配时明确报错，原始评审保存为 `judge-*-error.json`。

如果首次评审漏答或错配，系统会自动带纠偏指令重试一次；第二次成功时保留 `_previous_failed_attempts`，两次都失败才中止，避免丢弃已经生成的图片。JSON 截断/解析失败同样进入重试。

左右手评审要求先判断人物朝向，再按人物自身解剖左右与画面位置锚点核对；理由限制为最终结论，禁止反复改口和自我对话。

默认重复策略为 `JUDGE_REPEATS=10`：10 个请求不限制 Judge 内并发，任一有效评审失败都会中止；检查项、G-PQ、布局、编辑 SC/E-PQ 和参考 CP/PF 分别取众数，数值平票取较低分。动态 VQA、全项率、最低项和编辑 Overall 由众数后的原始字段重算；保持要求仅逐项检查，不再单独汇总 `preservation_score`。OCR 不重复。全部原始响应与分布保存在 judge JSON 中。"""

from .judge import VLMJudge
from .repeated import RepeatedVLMJudge

__all__ = ["RepeatedVLMJudge", "VLMJudge"]
