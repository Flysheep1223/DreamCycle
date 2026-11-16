# CLIPScore

## 一句话介绍

用冻结 CLIP 的图像、文本向量余弦相似度衡量语义匹配，是最常用的**参考自由、单样本图文对齐基线**之一；它不是美感、画质或细粒度组合正确率。

- **输入**：一张图 `v` 和一段文本 `c`
- **输出**：通常越高越好；原文将余弦截断并缩放，很多实现直接报告未缩放 cosine
- **是否需要真实参考图**：否
- **常见 backbone**：原论文 CLIP ViT-B/32；其他 CLIP/OpenCLIP 模型的分数不可直接混用

## 定义

原论文 CLIPScore 为：

`CLIP-S(c,v) = 2.5 * max(cos(E_txt(c), E_img(v)), 0)`

语料分数是样本均值。原文这样缩放是因为观察到的 cosine 多在约 0–0.4，希望把分布拉伸到近似 0–1；**这不意味着它是概率，也不意味着最高必为 1**。

`RefCLIPScore` 是面向图像描述任务的带参考扩展，把候选描述与参考描述的和谐平均等信息纳入；评测文生图时通常说的是不带参考的 `CLIP-S`，两者不要混淆。

## 评分流程

1. 使用 CLIP 对应预处理将图像缩放到规定尺寸并归一化。
2. 用同一 CLIP checkpoint 分别编码 prompt 与图像。
3. L2 归一化特征，算点积/余弦。
4. 按所选实现做 `2.5*max(x,0)` 或直接保留 cosine；对测试集取均值。
5. 报告中写清 backbone、权重、prompt 是否加模板、数值缩放和每 prompt 图数。

## 适用与配套数据

- 可用于 COCO Captions、DrawBench、PartiPrompts 或内部 prompt 集上的粗略语义回归。
- 常用于 DreamBench 中的 **CLIP-T**，表示生成图与目标文本的对齐；这与生成图和参考图的 CLIP-I 不同。
- 不需要标注参考答案，推理便宜，适合大量样本初筛。

## 优点

- 简单、快速、开源实现多；无需 LLM 问题生成或 VQA 多次推理。
- 对整体主题、常见对象和显著语义通常有效。
- 同一固定 checkpoint 下，可做同 prompt 候选图的粗排序。

## 局限与常见误用

- **bag-of-concepts 倾向**：可能看见“红 cube、蓝 sphere”所需概念便给高分，却把颜色绑错对象。
- 对数量、空间关系、否定、细粒度文字拼写、长 prompt 的各条件覆盖不可靠。
- CLIP 文本长度和视觉分辨率有限；prompt 截断、中心裁剪会改变分数。
- 分数受 backbone、训练数据、预处理、prompt 模板影响，不能跨实现比较绝对值。
- 高分可能来自训练分布中的常见搭配，而非每个条件被满足；也不代表更少伪影。
- 只用 CLIPScore 排模型，可能偏向“容易被 CLIP 看懂”的输出，而非人最喜欢的输出。

## 与其他指标的关系

CLIPScore 适合作为低成本 baseline。细粒度语义建议加 [VQAScore](../03_VQAScore/)、[Soft-TIFA](../07_GenEval2_SoftTIFA/) 或 [DSG](../05_DSG/)；综合偏好看 [PickScore](../../02_preference/01_PickScore/)，但它们共享视觉语言模型盲区，仍需人工校验。

## 官方来源与实现

- Hessel et al., **CLIPScore: A Reference-free Evaluation Metric for Image Captioning**, EMNLP 2021：[论文](https://aclanthology.org/2021.emnlp-main.595/)，[arXiv](https://arxiv.org/abs/2104.08718)
- 作者实现：[jmhessel/clipscore](https://github.com/jmhessel/clipscore)
- OpenCLIP：[mlfoundations/open_clip](https://github.com/mlfoundations/open_clip)

> 复现提示：优先记录 checkpoint 的完整名称与哈希。若写“CLIPScore=0.32”却未写 backbone、是否乘 2.5 和 prompt 集，该数字几乎不可审计。
