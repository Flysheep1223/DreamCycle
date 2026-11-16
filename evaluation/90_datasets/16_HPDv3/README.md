# HPD v3

## 数据卡

- **任务**：覆盖高低质量、不同模型代际的宽谱人类偏好学习。
- **规模**：**1.08M text-image pairs、1.17M annotated pairwise comparisons**。
- **图像来源**：新旧生成模型、MidJourney、curated HPDv2，以及 **57,759 张高质量真实图**（VLM captions）。
- **标注字段**：`choice_dist`、标注置信度、偏好/非偏好图像路径、模型来源等；训练还整合部分 Pick-a-Pic 与 ImageReward。

## 适合指标

[HPS v3](../../02_preference/03_HPSv3/) 的训练、成对准确率与不确定性研究。测试其他偏好模型时，应披露其训练是否已经包含 HPDv3 或其组成数据。

## 优点与局限

相比只含旧模型差图的数据，更适合区分强模型之间的细微质量差异；但整合多个公开偏好源会造成交叉验证不独立，真实图 caption 与用户 prompt 也有分布差异。偏好仍反映标注人群和来源模型。

## 来源

- 论文：[HPSv3, ICCV 2025](https://arxiv.org/abs/2508.03789)
- 官方数据：[MizzenAI/HPDv3](https://huggingface.co/datasets/MizzenAI/HPDv3)
- 官方代码：[MizzenAI/HPSv3](https://github.com/MizzenAI/HPSv3)
