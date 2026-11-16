# MHP（Multi-dimensional Human Preference Dataset）

## 数据卡

- **任务**：多维文生图人类偏好学习。
- **规模**：**918,315 条人类偏好标注、607,541 张图**。
- **维度**：Overall、Aesthetics、Semantic Alignment、Detail Quality。
- **对应模型**：MPS，通过 preference condition 控制评分维度。

## 适合指标

[MPS](../../02_preference/05_MPS/) 及各维度的成对偏好预测，也可用于研究多目标奖励优化。总体偏好与子维度冲突应保留，而不是强行合成唯一标签。

## 发布限制

官方 MPS 仓库截至整理日仅公开 **Overall checkpoint**，完整多维模型仍标为待发布。因此“数据集有四维”不等于“公开模型四个维度都可复现”；使用前检查最新 release。

## 来源

- Zhang et al., **Learning Multi-dimensional Human Preference for Text-to-Image Generation**, CVPR 2024：[论文](https://openaccess.thecvf.com/content/CVPR2024/papers/Zhang_Learning_Multi-Dimensional_Human_Preference_for_Text-to-Image_Generation_CVPR_2024_paper.pdf)
- 官方代码与发布说明：[Kwai-Kolors/MPS](https://github.com/Kwai-Kolors/MPS)
