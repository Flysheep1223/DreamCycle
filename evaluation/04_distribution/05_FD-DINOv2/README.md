# FD-DINOv2（Fréchet Distance with DINOv2 Features）

## 一句话介绍

保留 Fréchet Distance 的高斯分布距离公式，但将 Inception 特征换成 DINOv2 自监督视觉特征，以减轻 ImageNet 分类器表示对生成模型评价的偏差。

- **输入**：真实/参考图集与生成图集
- **常用特征**：Stein et al. 采用 DINOv2 ViT-L/14 等丰富视觉表示
- **输出**：越低越好，与 FID-Inception 数值不可直接比较
- **别名**：FDD、`FD_DINOv2`；报告中需展开特征与层

## 公式

设 DINOv2 特征的均值和协方差为 `(μ_r,Σ_r)`、`(μ_g,Σ_g)`：

`FD-DINOv2 = ||μ_r-μ_g||² + Tr(Σ_r+Σ_g-2(Σ_rΣ_g)^(1/2))`

因此它改变的是**表示空间**，没有消除 FID 的高斯假设和有限样本问题。

## 研究动机

Stein et al. 在 NeurIPS 2023 的系统研究中指出，一些常用指标没有充分反映扩散模型在人类感知真实性上的优势，问题很大程度上与 Inception-V3 特征有关。DINOv2 提供更通用的自监督视觉表示，可在此基础上计算 FD、Precision/Recall 及 memorization 等相关分析。

## 优点

- 自监督特征通常比 ImageNet 单标签分类特征覆盖更多对象、纹理与结构。
- 可复用成熟的 FD 统计和代码思路，易于与 FID 做特征消融。
- 对生成模型感知真实性的人类判断通常比旧 Inception 表示更合适。

## 局限

- **仍不是单图文图对齐指标**，不读取 prompt。
- 高斯假设、样本量偏差、resize/JPEG 敏感性仍然存在。
- DINOv2 模型大小、层、patch/class token、 pooling、归一化都会改变数值；目前没有像经典 FID 那样唯一的跨论文默认口径。
- 特征更通用并不表示对所有生成伪影、文字和人体结构都敏感。
- 与 CMMD 的选择应视为“FD + DINOv2”与“MMD + CLIP”的整体差异，不能只看 backbone 新旧。

## 推荐报告

`FD-DINOv2 / exact backbone / feature layer & pooling / N / reference split / resize / implementation commit`。若无法保证相同配置，优先只在同一实验内部比较，不引用他人绝对值。

## 来源与实现

- Stein et al., **Exposing Flaws of Generative Model Evaluation Metrics and Their Unfair Treatment of Diffusion Models**, NeurIPS 2023：[论文 PDF](https://proceedings.neurips.cc/paper_files/paper/2023/file/0bc795afae289ed465a65a3b4b1f4eb7-Paper-Conference.pdf)
- Oquab et al., **DINOv2: Learning Robust Visual Features without Supervision**：[论文](https://arxiv.org/abs/2304.07193)
- DINOv2 官方模型：[facebookresearch/dinov2](https://github.com/facebookresearch/dinov2)
- 可自定义特征的统计实现：[clean-fid](https://github.com/GaParmar/clean-fid)、[torch-fidelity](https://github.com/toshas/torch-fidelity)

> 本卡将 FD-DINOv2 视为一种特征化 FD 家族，而非宣称所有仓库共享一个官方唯一实现；复现时应以所用论文的代码为准。
