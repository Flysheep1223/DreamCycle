# VisionRewardDB-Image

## 数据卡

- **任务**：细粒度、多维视觉人类偏好学习。
- **图像规模**：官方仓库标为约 **48K × 60 dimensions**；视频另为约 33K × 64，不要混入图像卡。
- **标注形式**：层次化检查问题的二值判断，覆盖质量、语义、细节等多个维度。
- **配套**：问题清单 `VisionReward_image_qa.txt` 与权重 `weight.json`。

## 适合指标

[VisionReward](../../02_preference/06_VisionReward/) 的逐问题 yes/no、加权和及多维一致偏好优化。也可分析各问题的标注一致性和权重敏感性。

## 优点与局限

比单一偏好标签更可解释，适合定位奖励变化来源；大量二值问题也可能相关重复、标注成本巨大，权重反映特定人群效用。训练后同源的偏好测试不完全独立。

## 来源

- 论文：[VisionReward](https://arxiv.org/abs/2412.21059)
- 官方代码：[THUDM/VisionReward](https://github.com/THUDM/VisionReward)
- 图像数据：[THUDM/VisionRewardDB-Image](https://huggingface.co/datasets/THUDM/VisionRewardDB-Image)
