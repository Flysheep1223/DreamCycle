# AGIQA-3K

## 数据卡

- **任务**：AI 生成图像的感知质量与文图对齐人工评价。
- **规模**：**2,982 张生成图**。
- **生成模型**：GLIDE、Stable Diffusion 1.5、SDXL、Midjourney、AttnGAN、DALL·E 2 等 6 个模型/版本（名称以数据卡为准）。
- **标注**： perceptual quality 与 text-to-image alignment 的主观质量分，可用于两类独立分析。
- **论文 split**：训练/验证/测试划分见官方，常用约 70%/10%/20%。

## 适合指标

验证 MUSIQ、CLIP-IQA、Q-Align、Aesthetic Predictor 及生成图专用 IQA；元指标用 [SRCC/PLCC/KRCC](../../08_human_statistics/05_Correlation/)，有时另报 RMSE。

## 优点与局限

同时有质量和对齐标签，能避免把自然照片 IQA 直接套到生成图；但规模和模型代际有限，训练/测试必须按官方 prompt/模型分组检查泄漏。它不是一个叫“AGIQA”的统一评分公式，而是人工数据库。

## 来源

- Li et al., **AGIQA-3K: An Open Database for AI-Generated Image Quality Assessment**：[论文](https://arxiv.org/abs/2306.04717)
- 官方数据：[lcysyzxdxc/AGIQA-3k-Database](https://github.com/lcysyzxdxc/AGIQA-3k-Database)
