# SSIM / MS-SSIM（Structural Similarity）

## 一句话介绍

SSIM 从局部亮度、对比度和结构三个方面比较配对图像，比纯 MSE/PSNR 更贴近结构感知；MS-SSIM 再在多尺度上聚合。

- **输入**：两张对齐、同尺寸图像
- **输出**：SSIM 通常约 -1 到 1，越高越好，相同为 1
- **适用**：恢复、压缩、重建和编辑背景保持
- **不适用**：没有唯一像素答案的开放生成

## SSIM 公式

对局部窗口 `x,y`：

`SSIM(x,y) = [(2μ_xμ_y+C1)(2σ_xy+C2)] / [(μ_x²+μ_y²+C1)(σ_x²+σ_y²+C2)]`

`C1=(K1L)²`、`C2=(K2L)²` 用于数值稳定，`L` 为像素动态范围。它可分解为：

- luminance：局部均值；
- contrast：局部标准差；
- structure：去均值、归一化后的相关性。

经典实现使用局部滑动窗口（常见 11×11 Gaussian、σ=1.5），整图取窗口均值。窗口、边界、数据范围和通道处理必须固定。

## MS-SSIM

在多个下采样尺度计算对比度/结构项，并在最高尺度加入亮度项，再按权重乘积聚合：

`MS-SSIM = l_M^{α_M} Π_j c_j^{β_j}s_j^{β_j}`

不同库的尺度数、指数权重与下采样滤波可能不同，SSIM 与 MS-SSIM 数值不能混用。

## 优点

- 比 PSNR 更关注局部结构和对比度，对轻度亮度/对比变化有更合理的响应。
- 无需训练模型，计算快、确定性强。
- 多尺度版能同时看 coarse structure 和细节。

## 局限

- 仍要求空间对齐；合理移动、形变、替换对象会被视为结构差异。
- 对高级语义、身份、文本拼写和生成式幻觉不敏感。
- 在编辑全图上，高 SSIM 可能意味着没有执行指令。
- 不同库在 Gaussian window、边界 padding、Y/RGB 和输入范围上会产生差异。

## 编辑中的正确用法

在未编辑区域计算，并与指令成功率共同报告。mask 边界需要明确是否膨胀，防止编辑泄漏到背景却被忽略；卷积窗口跨 mask 边界的处理也应公开。

## 来源与实现

- Wang et al., **Image Quality Assessment: From Error Visibility to Structural Similarity**, IEEE TIP 2004：[DOI](https://doi.org/10.1109/TIP.2003.819861)
- Wang, Simoncelli, Bovik, **Multi-scale Structural Similarity for Image Quality Assessment**, Asilomar 2003：[论文页面](https://www.cns.nyu.edu/~lcv/ssim/)
- 实现：[scikit-image SSIM](https://scikit-image.org/docs/stable/api/skimage.metrics.html)、[piq](https://github.com/photosynthesis-team/piq)、[TorchMetrics](https://torchmetrics.readthedocs.io/en/stable/image/structural_similarity.html)
