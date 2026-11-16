# PIE-Bench（Prompt-based Image Editing Benchmark）

## 一句话介绍

包含 700 张带人工编辑 mask 的图像与源/目标 prompt，用结构距离、背景 PSNR/SSIM/MSE/LPIPS、CLIP 文本对齐和推理时间，系统评价扩散编辑的“改对、保留、效率”。

- **数据**：700 张图，10 类编辑
- **场景**：animal、human、indoor、outdoor，含自然与人工场景
- **每条标注**：source prompt、target prompt、editing instruction、编辑主体、人工编辑 mask
- **核心优点**：有 mask，能把编辑区外保持从全图相似度中分离

## 十类编辑

Random、Change Object、Add Object、Delete Object、Change Attribute、Change Count、Change Background、Change Style、Change Action、Change Position。不同资料对类别名有概括差异，复现以官方 annotation 文件为准。

## 四层评分

| 方面 | 指标 | 方向 |
|---|---|---|
| Structure preservation | DINO-ViT 自相似 Structure Distance | 越低越保持结构 |
| Background preservation | mask 外 PSNR、SSIM | 越高越好 |
| Background preservation | mask 外 MSE、LPIPS | 越低越好 |
| Edit fidelity | 全图及编辑区域 CLIP 文本相似度 | 越高越好 |
| Efficiency | 单图推理时间 | 越低越好；需同硬件/预算 |

## 推荐计算顺序

1. 按 source prompt/编辑指令生成输出，不更改官方 mask。
2. 检查源图与输出图尺寸及 mask 对齐。
3. 在 mask 外计算背景指标；全图/编辑区计算目标文本 CLIP。
4. 按 10 类编辑分别聚合，再给总体；记录每类有效样本数。
5. 同时查看编辑成功与背景保持，避免原图直出得到优秀“保持”成绩。

## 优点

- 同时覆盖多种局部/全局编辑，并提供精细人工 mask。
- 指标可解释且成本较低，适合 inversion/editing 方法的细粒度比较。
- 保留源/目标 prompt，可使用 Directional CLIP 等扩展。
- 结构、背景、文本、效率四维比单一 CLIP 分更全面。

## 局限

- 700 张规模有限，主要服务扩散 inversion 类编辑；复杂真实用户指令、多轮和多参考覆盖不足。
- CLIP 文本对齐不能可靠验证计数、复杂关系和文字渲染。
- mask 外指标要求空间对齐；扩散重绘的合理纹理差异仍会被惩罚。
- 不应将各指标未经校准地相加；应看分项或 Pareto。
- 不同实现对 mask dilation、LPIPS mask 和结构距离预处理需固定。

## 官方来源

- Ju et al., **Direct Inversion / PnP Inversion: Boosting Diffusion-based Editing with 3 Lines of Code**：[论文](https://arxiv.org/abs/2310.01506)
- 官方项目与数据入口：[cure-lab.github.io/PnPInversion](https://cure-lab.github.io/PnPInversion/)
- 官方代码：[cure-lab/PnPInversion](https://github.com/cure-lab/PnPInversion)
