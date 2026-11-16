# Pick-a-Pic v1 / v2

## 数据卡

- **任务**：真实用户文生图成对偏好学习与评审器验证。
- **v1**：PickScore_v1 使用的原始数据，约 50 万条偏好示例。
- **v2**：后续超过 **100 万条示例**；不是 PickScore_v1 的训练集。
- **字段**：prompt、两张候选生成图、用户选择/可能的 tie、图像或图像字节等；以 dataset revision 为准。

## 适合指标

训练/验证 [PickScore](../../02_preference/01_PickScore/)、HPS、ImageReward 等；在同 prompt 两图上计算成对偏好准确率，tie 按原协议处理。

## 优点与局限

来自真实文生图用户交互，比纯专家模拟更接近使用行为；但用户群、当时生成模型、界面和抽样方式带来偏好偏差。公开数据中的旧 URL 可能失效，官方建议用 Hugging Face 图像版本，下载体积极大。

## 数据隔离

训练奖励模型后，不能只在与训练同源的测试对上宣称独立泛化；应另用 HPD/ImageReward 或新人工偏好集验证，并记录去重规则。

## 来源

- Kirstain et al., **Pick-a-Pic**, NeurIPS 2023：[论文](https://arxiv.org/abs/2305.01569)
- [v1 数据](https://huggingface.co/datasets/yuvalkirstain/pickapic_v1)、[v2 数据](https://huggingface.co/datasets/yuvalkirstain/pickapic_v2)
- 官方代码：[yuvalkirstain/PickScore](https://github.com/yuvalkirstain/PickScore)
