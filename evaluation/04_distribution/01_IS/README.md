# IS（Inception Score）

## 一句话介绍

用 ImageNet Inception 分类器同时奖励“每张生成图类别明确”和“整个生成集类别多样”，是早期 GAN 常用指标；对现代开放式文生图通常只能作历史基线。

- **输入**：一组生成图，不需要真实参考图
- **输出**：大于 0，越高越好；不是概率
- **分类器**：经典为 Inception v3
- **测量目标**：条件类别可辨识性 + 边缘类别多样性，不是 prompt 对齐

## 公式

对生成图 `x_i`，分类器输出 `p(y|x_i)`，生成集边缘分布：

`p̂(y) = (1/N) Σ_i p(y|x_i)`

则：

`IS = exp( (1/N) Σ_i KL[p(y|x_i) || p̂(y)] )`

若单图预测非常尖锐（条件熵低），而整集类别又很均匀（边缘熵高），KL 均值大，IS 高。实践中常将样本分成若干 split 分别计算，再报均值和标准差；split 数和 N 必须记录。

## 适用数据

最适合与分类器训练域相近、标签明确的封闭域生成任务，例如 CIFAR/ImageNet 类生成。对于 COCO、DrawBench、多对象场景、艺术风格或文字海报，ImageNet 单标签分类无法表达主要目标。

## 优点

- 不需要真实参考集，计算和解释相对简单。
- 能同时惩罚一部分完全不可识别输出和整集只生成少数类别的模式坍缩。
- 有大量历史结果，可在完全同协议下做旧模型对照。

## 局限

- **不使用 prompt**：图像与文本完全无关也可能得高分。
- ImageNet 类别偏差明显；多对象、复杂关系和非写实图像不适用。
- 生成真实类别之外的合理图像可能被低分，生成分类器熟悉的简单对象可能被高分。
- 不需要真实分布，因此无法判断生成集是否覆盖真实数据的真实类别/属性比例。
- 受样本数、Inception 实现、resize、JPEG、split 影响；不能跨协议比较。
- 在现代文生图报告中不建议单独使用，更不应与 FID/CLIPScore 平均成总分。

## 官方来源与实现

- Salimans et al., **Improved Techniques for Training GANs**, NeurIPS 2016：[论文](https://arxiv.org/abs/1606.03498)
- 常用统一实现：[torch-fidelity](https://github.com/toshas/torch-fidelity)、[clean-fid](https://github.com/GaParmar/clean-fid)（FID/KID 为主；IS 需核对具体支持）
- 分析参考：Barratt & Sharma, **A Note on the Inception Score**：[论文](https://arxiv.org/abs/1801.01973)

> 若评测目标是通用文生图，优先把时间投入 Soft-TIFA/VQAScore、CMMD/FID（有参考时）和人工偏好，而不是 IS。
