# Masked Preservation（编辑区域外保持评分）

## 一句话介绍

利用编辑 mask 将“应该变化的区域”与“不应变化的区域”分开，在背景/未编辑区计算 PSNR、SSIM、MSE、LPIPS 等，避免全图相似度把正确编辑也当成错误。

- **输入**：源图、编辑图、编辑区域 mask
- **输出**：背景 PSNR/SSIM 越高越好；背景 MSE/LPIPS 越低越好
- **常见基准**：PIE-Bench
- **必须配套**：编辑成功率，否则原图直出会获得完美保持分

## 基本定义

设 `M=1` 为允许编辑区，`U=1-M` 为应保持区：

`MSE_bg = Σ_p U_p ||x_p-y_p||² / Σ_p U_p`

`PSNR_bg = 10 log10(L²/MSE_bg)`

SSIM 可在背景区域按约定窗口聚合；LPIPS 则必须说明 mask 在网络哪一层、如何归一化，因为深层感受野会跨越 mask 边界。

## 结构保持

PIE-Bench 还使用基于 DINO-ViT 自相似关系的 **Structure Distance**：比较源图与输出图内部 patch 间结构关系，而不只是要求相同位置像素一致。它对姿态/外观变化更宽容，但仍需结合背景指标与文本编辑成功判断。

## 评分建议

1. 检查源图与输出图尺寸、方向和色彩空间是否对齐。
2. 明确 mask 由人工标注、模型预测还是指令自动定位；人工 mask 与自动 mask 是不同协议。
3. 处理边界：mask dilation 可减少编辑泄漏被算入背景，但 dilation 大小会改变结果。
4. 分别报 PSNR_bg、SSIM_bg、LPIPS_bg/MSE_bg，不能只选一个有利项。
5. 对全图编辑、空 mask、完全遮挡等样本标 N/A，并给有效样本数。
6. 与编辑指令成功率构成二维图或 Pareto 曲线，不将两轴任意加权。

## 优点

- 直接量化“非目标区域是否被破坏”，是编辑评价不可缺少的一轴。
- 无需语义模型即可发现颜色漂移、背景重绘和全局失真。
- mask 使不同编辑类型可以采用一致协议。

## 局限

- mask 错误会系统性误评；复杂编辑的合理影响范围本身可能不唯一。
- 高背景保持不表示主体身份保持，也不表示指令已执行。
- PSNR/SSIM 仍要求对齐；扩散模型即使语义相同也可能重绘纹理，导致低分。
- 深度 LPIPS mask 的实现差异很大，跨仓库数值不应直接比较。
- 对全局风格变换，“背景”概念可能失效，应使用专门的全局编辑协议。

## 推荐组合

`编辑成功率（VIEScore/GEdit/人工） + 背景 LPIPS/PSNR/SSIM + 感知质量`。主体驱动编辑再加 DINO-I/CLIP-I；文字编辑再对目标文字和背景分别评分。

## 来源

- Ju et al., **Direct Inversion: Boosting Diffusion-based Editing with 3 Lines of Code / PIE-Bench**, NeurIPS 2023：[论文](https://arxiv.org/abs/2310.01506)
- 官方项目与数据入口：[cure-lab.github.io/PnPInversion](https://cure-lab.github.io/PnPInversion/)
- 相关单项：[PSNR](../01_PSNR/)、[SSIM](../02_SSIM/)、[LPIPS](../03_LPIPS/)
