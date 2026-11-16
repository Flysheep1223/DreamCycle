# ImageReward

## 一句话介绍

以 BLIP 为骨干、在约 13.7 万组专家图像比较上训练的通用文生图人类偏好奖励模型，可对单图给标量分或对同 prompt 多图排序。

- **输入**：prompt + 图像
- **输出**：标量 reward，越高越偏好；无统一概率解释
- **backbone**：BLIP 图像编码器、文本编码器与跨模态交互，后接 MLP 头
- **数据**：ImageRewardDB / 论文偏好标注

## 数据与训练

官方论文口径为 **8,878 条 prompt、136,892 对图像比较**（常四舍五入为 137k pairs），另有 466 条 prompt 留作测试。标注流程不仅给最终偏好，还包含对图像问题的反馈，用于提高标注质量。训练时冻结部分 BLIP 层，再学习从图文交互表示到标量偏好。

它与普通 BLIPScore 的区别是：BLIPScore 使用预训练图文匹配；ImageReward 显式用生成图的人类比较监督微调整个奖励模型。

## 评分流程

1. 加载官方 `ImageReward` checkpoint。
2. 输入原始 prompt 与图像，获得 `model.score(...)` 标量。
3. 对同 prompt 多图使用 `inference_rank(...)` 得到排序和奖励。
4. 模型横评时固定 prompt/生成预算并求均值；偏好预测验证时在 held-out 成对数据上算准确率。
5. 保存包版本、checkpoint 和原始分，不归一化成百分制。

## 优点

- 早期通用文生图偏好模型之一，开源、API 简单、使用广。
- 同一模型可用于评测、best-of-N 筛选和 ReFL 等偏好优化研究。
- 同 prompt 排序比只看图文 cosine 更接近综合人类选择。
- 公开偏好数据也可作为其他评审器的外部测试集。

## 局限

- 训练图像主要来自较早一代扩散模型和 DiffusionDB 分布，对新模型、新风格和多语言的泛化需重新验证。
- 一个标量混合文图对齐、审美、伪影等，不具备细粒度可解释性。
- 绝对分不跨 prompt 校准，也不能与 PickScore/HPS 的绝对值比较。
- 被用作训练奖励时容易产生过优化；应保留独立偏好分、语义指标和人工评审。
- “137k pairs”是专家比较数，不是独立 prompt 数或图像总数。

## 官方来源与调用

- Xu et al., **ImageReward: Learning and Evaluating Human Preferences for Text-to-Image Generation**, NeurIPS 2023：[论文](https://arxiv.org/abs/2304.05977)
- 官方代码：[THUDM/ImageReward](https://github.com/THUDM/ImageReward)
- 数据：[THUDM/ImageRewardDB](https://huggingface.co/datasets/THUDM/ImageRewardDB)
- 包：[PyPI image-reward](https://pypi.org/project/image-reward/)

```python
import ImageReward as RM
model = RM.load("ImageReward-v1.0")
score = model.score("a red cube beside a blue sphere", "image.png")
ranking, rewards = model.inference_rank("a red cube", ["1.png", "2.png"])
```

> 报告格式：`ImageReward-v1.0 / prompt set / K images per prompt / mean raw reward`。
