# HPS v2 / HPS v2.1（Human Preference Score v2）

## 一句话介绍

在 HPD v2 大规模人类偏好数据上训练的 CLIP 系偏好预测器，并提供 Animation、Concept-art、Painting、Photo 四种风格的固定 benchmark prompts。

- **输入**：prompt 与同 prompt 的生成图
- **输出**：标量偏好分，越高越好；不是概率
- **版本**：v2.0 与 v2.1 分数不能直接比较
- **官方提醒**：比较主要对**同一 prompt**的图像有意义

## 数据与模型

HPD v2 官方 README 的口径为：

- 约 **798k 次成对偏好选择**；
- 超过 **430k 张图像**；
- 约 **107k 条 prompt**；
- 约 **645k train pairs / 153k test pairs**。

图像来自多个文生图模型及 COCO Captions，prompt 来源包括 DiffusionDB 与 MSCOCO。注意：430k 是图像数，不应误写成“433k 图像对”。

HPS v2 在 CLIP 架构上学习偏好；v2.1 使用更高质量数据及 HPD v2.0 train split 再训练。两者原始输出尺度不同。

## 评分方式

1. 固定 `hps_version="v2.0"` 或 `"v2.1"`。
2. 对图像和 prompt 前向计算标量分。
3. 同 prompt 多图时按分数排序；模型横评时按 prompt/风格聚合平均分。
4. 官方 benchmark 分别报告四种风格及平均，不只报总均值。
5. 偏好预测器本身可在 HPD v2、ImageReward、Pick-a-Pic 测试集上算成对准确率，但这属于“评审器与人的吻合度”，不是生成模型的 HPS 分。

## HPS 风格 benchmark

官方提供四类固定 prompt 和图像目录规范：

- Animation
- Concept-art
- Painting
- Photo

另提供 DrawBench 相关入口。不同风格分开发布能避免模型只靠某一风格占优势；仍不能替代组合、文字、知识等专项测试。

## 优点

- 训练数据规模大、人工选择多，跨多个生成模型和风格。
- 同 prompt 排序与固定 prompt benchmark 均有官方代码，易复现。
- HPD v2 同时可用于验证其他偏好模型的人机一致性。
- 四类风格分项比单个整体分更有诊断性。

## 局限

- 偏好数据以当时生成模型和用户标注分布为主，对新一代模型和真实用户群可能漂移。
- 原始分不是跨 prompt 校准概率，不应把 28 分解释为“28% 人喜欢”。
- v2.0/v2.1 不可直接比较，其他 HPS/HPS v3 也不是同一尺度。
- 单一分数混合对齐、质量和风格偏好，无法独立证明数量或空间正确。
- 用于训练 reward 后应保留独立评测，防止过拟合评审器。

## 官方来源与使用

- Wu et al., **Human Preference Score v2: A Solid Benchmark for Evaluating Human Preferences of Text-to-Image Synthesis**：[论文](https://arxiv.org/abs/2306.09341)
- 官方代码：[tgxs002/HPSv2](https://github.com/tgxs002/HPSv2)
- 数据：[ymhao/HPDv2](https://huggingface.co/datasets/ymhao/HPDv2)

```python
import hpsv2
result = hpsv2.score(["1.png", "2.png"], "a cat with two horns", hps_version="v2.1")
hpsv2.evaluate("<images_path>", hps_version="v2.1")
```

> 报告示例：`HPS v2.1, official benchmark prompts, 1 image/prompt, mean by four styles`。
