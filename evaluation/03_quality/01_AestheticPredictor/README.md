# LAION Aesthetic Predictor / Aesthetic Score

## 一句话介绍

在 CLIP 图像 embedding 上用人工美学评分训练一个轻量预测头，估计“照片/图片是否美观”；它不读取生成 prompt，因此不衡量文图对齐。

- **输入**：单张图像
- **输出**：常见实现给近似 1–10 的回归分，越高越美观；并非概率，也不保证严格有界
- **常用基础特征**：CLIP ViT-L/14
- **关键风险**：名称相同但 V1、V2、improved predictor 的数据和预测头不同

## 模型与版本

LAION 官方介绍的版本包括：

- **V1**：以约 5,000 个 SAC（Simulacra Aesthetic Captions）图像评分对训练，CLIP embedding 上的轻量/线性预测器。
- **V2**：训练来源扩展到 SAC（约 176k 图像评分对）、LAION-Logos（约 15k）与 AVA（约 250k 照片及 1–10 评分）等。
- 社区常用的 **improved-aesthetic-predictor** 是另一种广泛复现实现，常采用 CLIP embedding 上的 MLP。使用时必须记录具体仓库与 `.pth/.safetensors`，不能只写“Aesthetic Score”。

抽象形式：`a = MLP_or_linear(CLIP_image(x))`。模型只看图像，不知道用户想要什么内容。

## 评分流程

1. 固定 CLIP backbone、权重和图像预处理。
2. 固定美学预测头 checkpoint。
3. 逐图计算 aesthetic score，在 prompt/测试集取均值或分布。
4. 同时保存中位数、低分比例，避免极端值只被均值掩盖。
5. 与文图对齐和伪影指标联合报告。

## 配套数据

- **AVA**：摄影美学评分，训练的是自然照片偏好。
- **SAC**：针对 AI 生成图像收集的美学评分，更贴近生成图域。
- **LAION-Logos**：Logo 美学，但规模较小、领域特殊。
- **AGIQA-3K** 等带生成图人工质量分的数据可做外部验证，但不是所有 Aesthetic Predictor 的训练集。

## 优点

- 极快、参考自由、无需 prompt，适合海量图片过滤和粗排。
- 对整体色彩、构图、常规摄影美感有一定指示作用。
- 开源且易嵌入数据清洗管线。

## 局限

- **美学不等于技术质量**：一张风格化、低保真但美观的图可能高分；伪影也不一定被充分惩罚。
- **美学不等于对齐**：可以生成与 prompt 无关但漂亮的图得高分。
- 数据偏置会影响肤色、文化、非写实风格、文字海报、极简设计等判断。
- 用其作为筛选/训练奖励会强化单一审美，降低风格多样性。
- 不同 checkpoint 的分值尺度、训练标签与 CLIP 版本不同，不能跨实现比较。

## 官方来源

- LAION 官方介绍：[LAION-Aesthetics](https://laion.ai/blog/laion-aesthetics/)
- 官方基础实现：[LAION-AI/aesthetic-predictor](https://github.com/LAION-AI/aesthetic-predictor)
- 常用 improved 实现：[christophschuhmann/improved-aesthetic-predictor](https://github.com/christophschuhmann/improved-aesthetic-predictor)
- AVA 数据集论文：Murray et al., **AVA: A Large-Scale Database for Aesthetic Visual Analysis**, CVPR 2012：[DOI](https://doi.org/10.1109/CVPR.2012.6247954)（数据下载与许可需核对官方渠道）

> 建议报告 `checkpoint + CLIP backbone + mean/median + prompt set`，并至少搭配一个文图对齐指标和一个人工/生成图质量指标。
