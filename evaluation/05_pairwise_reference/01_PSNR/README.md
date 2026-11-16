# PSNR（Peak Signal-to-Noise Ratio）

## 一句话介绍

由配对图像的均方误差计算峰值信噪比，单位通常为 dB；适合像素严格对齐、存在唯一目标图的恢复/重建任务，不适合评判开放式文生图的多种合理答案。

- **输入**：输出图与同尺寸参考目标图
- **输出**：越高越好；完全相同可趋于无穷大
- **方向**：MSE 越低 → PSNR 越高
- **常见使用**：超分、去噪、压缩、图像恢复；编辑任务中只算未编辑背景

## 公式

若像素范围为 `[0,L]`，8-bit 图像 `L=255`，归一化到 `[0,1]` 时 `L=1`：

`MSE = (1/(C H W)) Σ_cΣ_hΣ_w (x_chw-y_chw)²`

`PSNR = 10 log10(L²/MSE)`

MSE=0 时应单独处理，不能因浮点除零丢失样本。报告中需说明 RGB 三通道还是只算 Y/luma、像素范围、颜色空间与裁剪边界。

## 编辑背景版本

设应编辑区域 mask 为 `M`，未编辑区域 `U=1-M`：

`MSE_bg = Σ U(x-y)² / Σ U`

再代入 PSNR。若 mask 为空或全图都要求编辑，该值无定义，应标记 N/A 而非记为 0。

## 优点

- 定义简单、确定、低成本，不需要神经网络。
- 对严格配准的像素误差和压缩/噪声变化敏感。
- 在相同分辨率、颜色空间与参考图下易复现。

## 局限

- **像素对齐要求强**：轻微平移、重构图或合理重绘都会被重罚。
- MSE 与人眼感知不完全一致；模糊图有时比清晰但略偏移的图 PSNR 更高。
- 开放式生成不存在唯一像素答案，因此 PSNR 低不等于生成质量差。
- 全图编辑 PSNR 会惩罚本应发生的变化；即使背景版也依赖准确 mask。
- RGB/Y、8-bit/归一化、边界裁剪和通道平均方式会改变 dB 数值。

## 推荐搭配

恢复任务与 SSIM/LPIPS 及人工质量搭配；编辑任务与编辑成功率搭配，防止“原图直出”获得最高保持分。不要用 PSNR 代替 CLIP/DINO 主体语义一致性。

## 来源与实现

- 经典图像质量评价背景：Wang et al., **Image Quality Assessment: From Error Visibility to Structural Similarity**, IEEE TIP 2004：[DOI](https://doi.org/10.1109/TIP.2003.819861)
- 实现：[scikit-image `peak_signal_noise_ratio`](https://scikit-image.org/docs/stable/api/skimage.metrics.html)、[TorchMetrics PSNR](https://torchmetrics.readthedocs.io/en/stable/image/peak_signal_noise_ratio.html)
