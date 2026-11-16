# HPS v3

## 一句话介绍

基于 Qwen2-VL 的宽谱人类偏好模型，训练数据同时覆盖新旧生成模型、高/低质量真实图，并用带不确定性的评分头预测偏好均值与方差。

- **backbone**：Qwen2-VL（官方 7B 配置）
- **输出**：奖励均值 `μ`，模型还可预测不确定性 `σ`
- **用途**：图像质量与 prompt 对齐的综合偏好、候选排序、奖励建模
- **不能混比**：HPS v3 与 v2.x 的原始分不是同一尺度

## HPD v3 数据

官方规模为：

- **1.08M text-image pairs**；
- **1.17M annotated pairwise comparisons**。

数据覆盖 FLUX.1 dev、SD3、Kolors、HunyuanDiT、Infinity、MidJourney、CogView4 等较新模型，也保留 SD1.x、CogView2、GLIDE 等早期模型；另含 **57,759 张高质量真实图**及 VLM captions。训练配置还整合经抽样的 Pick-a-Pic、ImageReward 与 curated HPD v2。这样设计是为了减少只会区分“旧模型差图”，却不会区分“新模型细微优劣”的问题。

## 模型与不确定性

HPS v3 从 Qwen2-VL 提取图文表示，经 MLP/奖励头得到：

`r ~ N(μ, σ²)`

排序训练不仅看均值差，还利用预测的不确定性处理难分或标注不一致样本。官方数据格式可含 `choice_dist` 与标注者能力相关的 `confidence`，训练时支持置信度过滤。推理通常取 `μ` 作为分数；`σ` 可用于标记评审器不确定的样本，但不应直接当人工分歧概率。

## 评分与 benchmark

官方提供人物、艺术、设计、建筑、动物、自然、交通、产品、植物、食物、科学等类别 benchmark，按类别及 Overall 报告。使用该 benchmark 时固定官方 prompt、生成数量和聚合代码；自建 prompt 上则报告均值、标准差及同 prompt 成对胜率。

偏好模型验证应分开报告：在 HPD v3、HPD v2、PickScore、ImageReward 测试集上的成对预测准确率。某个测试集与训练数据来源接近时，结果不能视作完全独立外部验证。

## 优点

- 宽谱数据同时含高质量新模型与低质量旧模型，更适合分辨细微差异。
- VLM 骨干比纯 CLIP 双编码器具备更丰富的跨模态表示能力。
- 显式不确定性提供质量控制和主动人工复核入口。
- 开源推理、训练、数据和 CoHP 迭代筛选代码。

## 局限

- 仍继承标注者、prompt、模型来源与 MidJourney 用户偏好的数据偏差。
- 训练整合了多个公开偏好集，在这些同源测试集上的高分需同时看独立人工验证。
- 综合奖励不解释具体组合错误，也不能替代 OCR/数量/空间等专项指标。
- 用 HPS v3 做 RL 或 best-of-N 选择后，再用同一 HPS v3 宣称提升会造成循环评价。
- VLM 推理成本高于 CLIP 系；不同版本权重、precision 和预处理应固定。

## 官方来源与使用

- Ma et al., **HPSv3: Towards Wide-Spectrum Human Preference Score**, ICCV 2025：[论文](https://arxiv.org/abs/2508.03789)
- 官方代码：[MizzenAI/HPSv3](https://github.com/MizzenAI/HPSv3)
- 模型：[MizzenAI/HPSv3](https://huggingface.co/MizzenAI/HPSv3)
- 数据：[MizzenAI/HPDv3](https://huggingface.co/datasets/MizzenAI/HPDv3)

```python
from hpsv3 import HPSv3RewardInferencer
inferencer = HPSv3RewardInferencer(device="cuda")
rewards = inferencer.reward([prompt], image_paths=["image.png"])
mu = rewards[0][0].item()
```
