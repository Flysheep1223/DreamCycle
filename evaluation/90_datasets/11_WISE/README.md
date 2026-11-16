# WISE 数据集（Original / Verified）

## 数据卡

- **任务**：世界知识驱动的文生图语义评价。
- **规模**：1,000 条 prompt、25 个子领域。
- **三大类**：文化常识、时空推理、自然科学；汇总为 Culture/Time/Space/Biology/Physics/Chemistry。
- **标注**：prompt 及解释，用于告诉 judge 期望的隐含知识答案。

## 两版差异

- **Original**：原始 prompt + GPT-4o-2024-05-13，Consistency/Realism/Aesthetic 各 0–2，原版 WiScore 加权。
- **WISE_Verified（2026默认）**：约 200 条 prompt 刷新，Qwen3.5-35B-A3B judge，单图二值 0/1，类别权重更新。

两版 prompt、judge 和分数不同，不可拼接趋势或混用榜单。

## 适合指标

[WiScore](../../01_alignment/10_WISE_WiScore/)，以及知识正确项的人工评价和“原 prompt→显式答案改写”对照分析。通用 CLIPScore 无法可靠区分“不知道知识答案”与“图像画错”。

## 来源

- 论文：[WISE](https://arxiv.org/abs/2503.07265)
- 官方 Original 归档与 Verified 数据：[PKU-YuanGroup/WISE](https://github.com/PKU-YuanGroup/WISE)
