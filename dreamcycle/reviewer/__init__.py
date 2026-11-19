r"""# reviewer 模块

`PromptAdvisor` 采用两次独立 VLM 调用：

1. **评估审计**：查看原始 Prompt、全部输入图和生成图、路由、逐项评分及理由、OCR、各分离指标和全项通过率，输出对当前评估的意见、补充检查项与可能的评审误判。
2. **独立 Prompt 改写**：只看不可变的用户原始需求、当前草稿与图像，不传入评分、评审理由、OCR、评估意见或争议检查项，避免被有问题的评估带偏。连续迭代采用原始需求锚定、最多两处等义澄清和字符预算，不新增可检查条件，防止把上一轮新增约束不断累积；超长时纠偏一次，仍超长则回退原始需求。

编辑任务只写目标修改与整体保持，不根据生成图臆造源图细节。原始返回记录 `prompt_revision_policy`（长度、预算、重试和回退状态）及 `prompt_suggestion_excluded_context`，便于审计改写上下文。

返回结果先给生成 Prompt 修改建议与改写版本，再给评估意见。审计器不修改原始分数，失败时主评分仍保留，错误写入 `advice-*-error.json`。

通过 `ADVISOR_ENABLED=false` 或 CLI `--no-advice` 关闭，以减少实时 VLM 调用。"""

from .advisor import PromptAdvisor

__all__ = ["PromptAdvisor"]
