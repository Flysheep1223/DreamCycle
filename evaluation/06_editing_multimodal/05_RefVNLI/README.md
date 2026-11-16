# RefVNLI

## 一句话介绍

一个面向主体驱动文生图的微调 auto-rater：一次输入 `<参考图, prompt, 目标图>`，连续预测 **Textual Alignment** 与 **Subject Preservation** 两个概率型分数。

- **backbone**：适配多图输入的 PaliGemma 变体
- **输出**：两个分数，分别对应文本对齐与主体保持
- **训练标签**：两个二值标签 `<alignment, preservation>∈{0,1}²`
- **目标**：降低 DreamBench++/VIEScore 等商业 GPT judge 的成本，同时比 CLIP-I/DINO-I 更关注身份关键细节

## 模型与推理

论文使用适配多图输入的 `paligemma-3b-ft-nlvr2-448` 类模型，prompt 中用标记指出被参考主体。模型依次做两个二分类：

1. 第一个生成 token 评 Textual Alignment；
2. 第二个生成 token 评 Subject Preservation。

推理时分别利用预测 `1` 与 `0` 的概率形成分数（论文描述为二者比率所构造的分数）。复现必须遵循论文附录中的精确变换，不应把 log-odds、概率比和概率本身混称。

## 训练数据构造

- 从视频帧中提取同一主体的正样本，以及同类别不同主体的负样本，让模型对姿态、背景、服装等非身份变化稳健。
- 对身份关键区域做 masking/inpainting，保持其他区域不变，构造困难负样本，使模型关注面部、形状、颜色等身份定义特征。
- 文本正样本描述参考主体；负样本通过同类实体间交换 prompt 或修改一个非主体细节构造。

## 元评价方式

论文把 DreamBench++ 等人工标注统一为文本对齐/主体保持二值标签，分别计算 **ROC AUC**，再用两项 AUC 的调和平均得到统一元评价分。这里的 AUC 衡量“评分器能否区分人工正负样本”，不是生成模型本身的准确率。

多主体评测中可将实例拆成各主体评价，并取较低分作为严格结果，避免一个主体正确掩盖另一个主体失败。

## 优点

- 单次运行同时输出两个核心维度，避免分别跑 CLIP-T 与 CLIP-I 的片面性。
- 困难负样本专门针对身份关键变化，理论上比整图 cosine 更少被背景相似欺骗。
- 开放 PaliGemma 骨干使大规模、低成本本地评审更有可能。
- 论文在多类主体和罕见概念人工数据上验证，报告了相对基线的改进。

## 局限与可用性

- 训练数据构造方式决定“身份”的定义；风格主体、抽象概念或多角色交互仍需额外验证。
- 二值训练标签丢失人工评分中的细粒度程度；输出分数不是人类满意度。
- 与所有学习评审器一样，存在领域偏差和被生成模型优化的风险。
- 截至本次查阅的论文 HTML 未给出独立官方 RefVNLI 代码/权重链接；实际复现前应再次查找作者发布，不能将基础 PaliGemma checkpoint 当成 RefVNLI。

## 官方来源

- Slobodkin et al., **RefVNLI: Towards Scalable Evaluation of Subject-driven Text-to-image Generation**, Findings of EMNLP 2025：[论文](https://arxiv.org/abs/2504.17502)
- 基础模型说明：[PaliGemma](https://huggingface.co/google/paligemma-3b-ft-nlvr2-448)

> 若无法取得官方微调权重，建议生产评测先用 DreamBench++/人工 + DINO-I/CLIP-I/VQAScore，而不是声称已复现 RefVNLI。
