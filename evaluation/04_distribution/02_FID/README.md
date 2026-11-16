# FID（Fréchet Inception Distance）

## 一句话介绍

将真实图和生成图的 Inception v3 特征分别近似为高斯分布，用两个高斯的 Fréchet 距离衡量集合分布差异；越低越好，但不是单图质量或文图对齐分。

- **输入**：生成图像集 + 参考图像集
- **经典特征**：Inception v3 pool3，2,048 维
- **输出**：`FID ≥ 0`，相同分布的理想值为 0，越低越好
- **关键变量**：样本数、参考 split、resize/quantization、特征权重、图像格式

## 公式

真实与生成特征的均值、协方差分别为 `(μ_r,Σ_r)`、`(μ_g,Σ_g)`：

`FID = ||μ_r-μ_g||² + Tr(Σ_r + Σ_g - 2(Σ_rΣ_g)^(1/2))`

它只完整匹配高斯假设下的一阶、二阶矩；真实特征若非高斯，FID 为 0 的充分直观解释仍需谨慎。

## 文生图常用协议

- COCO 2014 validation 是常见参考集，很多工作使用约 30k 个 prompt/生成样本与对应真实图。
- GAN 封闭域任务常见 50k 生成图；不同任务的 30k、50k 或 10k FID 不应直接横比。
- 参考图与生成图应按基准规定做 resize/crop；如果目标是比较 1024×1024 高分辨率生成，低分辨率 COCO 参考可能不合适。
- 报告 `N_gen/N_ref`、数据集 split、是否 center crop、resize、实现与 mode。

## Clean-FID 为什么重要

Clean-FID 论文显示，不同库的 bicubic/antialias、像素量化和 JPEG 处理会显著改变 FID，即使人眼几乎看不出差异。`clean-fid` 提供 `mode="clean"`，也提供 legacy PyTorch/TensorFlow 模式复现旧数。引用旧论文时，最好在同一代码下重新计算全部模型。

## 优点

- 同时反映整体保真与部分分布覆盖，历史上可比结果丰富。
- 无需人工逐图打分，适合固定数据域的模型回归。
- 对模式坍缩、明显域偏移和多种失真通常有响应。

## 局限

- 高斯近似、Inception 表示与有限样本偏差；小 N 下尤其不稳定。
- 不使用 prompt，即使 COCO 图与 caption 配对生成，FID 本身也不验证每条文本是否被满足。
- 真实参考域若与生成目标不匹配，低 FID 可能奖励复制参考风格而非任务成功。
- 可能对扩散模型的感知质量与人类排序反映不充分；不能只靠它评价现代生成模型。
- 对 resize、压缩、分辨率与统计缓存极敏感，随意下载“官方均值方差”可能用错 split。

## 推荐搭配

有匹配参考域时，与 [CMMD](../04_CMMD/) 或 KID 及 Precision/Recall 联合；语义另用 Soft-TIFA/VQAScore，偏好另用人工或奖励模型。报告多次子采样均值与区间，不只报一次小数。

## 官方来源与实现

- Heusel et al., **GANs Trained by a Two Time-Scale Update Rule Converge to a Local Nash Equilibrium**, NeurIPS 2017：[论文](https://arxiv.org/abs/1706.08500)
- Parmar et al., **On Aliased Resizing and Surprising Subtleties in GAN Evaluation**, CVPR 2022：[论文](https://arxiv.org/abs/2104.11222)
- 推荐实现：[GaParmar/clean-fid](https://github.com/GaParmar/clean-fid)、[torch-fidelity](https://github.com/toshas/torch-fidelity)

```python
from cleanfid import fid
score = fid.compute_fid("generated/", "reference/", mode="clean")
```
