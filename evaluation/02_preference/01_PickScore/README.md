# PickScore

## 一句话介绍

在真实文生图用户的成对偏好数据上微调 CLIP-H 得到的标量奖励模型，用于预测同一 prompt 下哪张图更可能被用户选择。

- **输入**：prompt 与一张或多张候选图
- **输出**：无界/任意缩放的偏好 logit；多图可经 softmax 转成相对选择概率
- **backbone**：`laion/CLIP-ViT-H-14-laion2B-s32B-b79K`
- **checkpoint**：`yuvalkirstain/PickScore_v1`，训练于 Pick-a-Pic v1

## 定义与训练

单图得分：

`s(x,y) = exp(logit_scale) * <E_txt(x), E_img(y)>`

其中图像、文本向量均做 L2 归一化。对同一 prompt 的候选图：

`P(y_i | x,{y}) = softmax_i(s(x,y_i))`

训练使用用户偏好分布 `p`：明确选图时为一热，tie 时可记为 `[0.5,0.5]`；通过偏好分布与模型 softmax 分布之间的 KL/交叉熵式目标优化，并在训练实现中使用批内负样本。这里的概率是**候选集合内相对概率**，不是单图绝对质量。

## 配套数据

- **Pick-a-Pic v1**：原论文与 PickScore_v1 使用的数据，规模通常概括为约 50 万条带用户偏好的图文生成示例。
- **Pick-a-Pic v2**：后续发布，超过 100 万条示例；**PickScore_v1 并未因此自动变成 v2 模型**。
- 每条比较包含 prompt、两张生成图、用户选择及可能的 tie 等字段；具体规模和字段以所用 HF dataset revision 为准。

## 评分与聚合

- 单图：保存原始 `score`，在测试集取均值；数值依赖 logit scale，不要解释成 0–100。
- 同 prompt 两图：较高分者作为预测偏好；与人工标签计算准确率，tie 规则单独说明。
- 多图：对 scores 做 softmax，报告候选集合；增加/删除候选会改变概率。
- 文生图模型横评：固定 prompt、采样预算和候选构造，再比较平均 PickScore 或胜率。

## 优点

- 直接学习真实文生图用户行为，而非只用图文检索相似度。
- 推理成本接近 CLIP，适合大规模自动筛选和同 prompt 候选排序。
- 原始论文在多个模型排序与用户 Elo 的相关分析中优于当时多种自动基线。

## 局限

- 训练数据反映当时用户、模型和界面分布，可能偏好某种色彩、风格或常见题材。
- 对最新模型、极端风格、多语言和专业任务的泛化需重新验证。
- 作为奖励优化目标时会发生 reward hacking：分数升高可能不再对应真实偏好。
- 一个总分难区分“没对齐”“不美观”“有伪影”；组合语义应另用 Soft-TIFA/GenEval 等。
- 不同 prompt 的绝对分不一定有共同尺度，最稳妥的是同 prompt 相对比较。

## 官方来源与最小实现

- Kirstain et al., **Pick-a-Pic: An Open Dataset of User Preferences for Text-to-Image Generation**, NeurIPS 2023：[论文](https://arxiv.org/abs/2305.01569)
- 官方代码：[yuvalkirstain/PickScore](https://github.com/yuvalkirstain/PickScore)
- 模型：[PickScore_v1](https://huggingface.co/yuvalkirstain/PickScore_v1)
- 数据：[v1](https://huggingface.co/datasets/yuvalkirstain/pickapic_v1)、[v2](https://huggingface.co/datasets/yuvalkirstain/pickapic_v2)

官方推理的关键为：`model.logit_scale.exp() * (text_embs @ image_embs.T)`，多图时再 `softmax(scores)`。报告时不要只写 softmax 后的概率而遗漏候选集合。
