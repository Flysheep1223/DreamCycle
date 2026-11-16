# ImageRewardDB

## 数据卡

- **任务**：文生图专家偏好学习与跨评审器验证。
- **规模**：**8,878 条 prompt、136,892 对图像比较**，常简称 137k pairs；466 条 prompt 留作测试。
- **内容**：DiffusionDB 相关 prompt/生成图及专家偏好比较，标注流程包含图像问题反馈。
- **对应模型**：ImageReward-v1.0。

## 适合指标

[ImageReward](../../02_preference/04_ImageReward/)、PickScore、HPS、MPS 等的成对偏好预测准确率。也可以研究奖励模型/ReFL，但训练后需另找独立人工测试。

## 优点与局限

公开、专家标注、使用广，便于不同评审器横向比较；局限是生成模型代际较早、单一综合偏好不够可解释，且多份新模型训练数据已整合它，不能再视为完全独立外部集。

## 来源

- Xu et al., **ImageReward**, NeurIPS 2023：[论文](https://arxiv.org/abs/2304.05977)
- 数据：[THUDM/ImageRewardDB](https://huggingface.co/datasets/THUDM/ImageRewardDB)
- 官方代码：[THUDM/ImageReward](https://github.com/THUDM/ImageReward)
