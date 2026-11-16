# EvalMuse-40K

## 数据卡

- **任务**：可靠、元素级文图对齐与结构问题评价。
- **规模**：**4,000 条 prompt、40,000 个图文样本、超过 100 万条细粒度人工标注**。
- **prompt**：2,000 条 DiffusionDB 真实 prompt + 2,000 条 GPT-4 合成 prompt；后者针对数量、颜色/材质、环境/时间、活动/视角、文字、空间组合等技能。
- **图像**：来自 20 个 T2I 模型，每 prompt 共 10 张图像样本。
- **标注**：整体与元素级对齐、生成图结构问题，并含复核/重标以提高可靠性。

## 配套评分方法

- **FGA-BLIP2**：端到端微调整体与元素级对齐分；
- **PN-VQA**：positive/negative 问题对的零样本细粒度 VQA 评价。

本资料库将其作为重要元评价数据集；具体公式与复现应以官方论文/代码为准，不与普通 VQAScore 混称。

## 来源

- Han et al., **EvalMuse-40K**：[论文](https://arxiv.org/abs/2412.18150)
- 项目页：[shh-han.github.io/EvalMuse-project](https://shh-han.github.io/EvalMuse-project/)
