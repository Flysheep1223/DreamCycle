# DINO-I / DINO Similarity

## 一句话介绍

用 DINO/DINOv2 自监督视觉特征比较参考主体与生成图，是个性化生成中常用的主体保持指标；与 CLIP-I 互补，但同样会受背景、裁剪和“没有编辑”影响。

- **输入**：参考图与生成图
- **输出**：特征 cosine，越高越相似
- **DreamBooth 原始设置**：DINO ViT 特征；后续工作也使用 DINOv2，必须区分
- **不使用文本**：只测视觉一致性

## 公式

`DINO-I = cos(E_DINO(x_ref), E_DINO(x_gen))`

DreamBooth 类方法通常取整图全局表示（如 class token/官方指定 pooled feature）。如果改用 patch tokens、主体框内平均或 DINOv2，应写成新协议并说明层与 pooling。

## 为什么与 CLIP-I 一起用

DINO 的自监督目标与 CLIP 的图文对比学习不同，通常对对象外观、形状和实例级视觉结构提供不同偏置。两者同高增强主体保持的证据；若一高一低，应检查主体裁剪、背景和风格变化，而不是简单平均掩盖。

## 优点

- 对像素级姿态和视角变化比 PSNR/SSIM 更宽容。
- 不依赖文本编码，可直接比较多张参考图。
- 与 CLIP-I/CLIP-T 形成较简洁的个性化生成评价组合。

## 局限

- 整图特征可能被大面积背景主导；主体丢失但场景相似仍可能高分。
- 不保证人脸识别级别的身份一致性，也不能可靠判断细节 Logo 或文字。
- 目标 prompt 要求改变风格/材质时，高 DINO-I 不一定总是好事，需明确哪些属性应保持。
- DINO v1/v2、ViT-S/B/L、层和 pooling 的分数不可直接比较。
- 单独优化会奖励复制参考或拒绝编辑。

## 推荐报告

`DINO-I / exact model & revision / CLS or patch pooling / full image or subject crop / reference aggregation`。同时报 CLIP-T/VQAScore 和人工主体保持判断；多主体时逐个主体评分，报告遗漏与串换。

## 来源

- Caron et al., **Emerging Properties in Self-Supervised Vision Transformers (DINO)**, ICCV 2021：[论文](https://arxiv.org/abs/2104.14294)
- Oquab et al., **DINOv2: Learning Robust Visual Features without Supervision**：[论文](https://arxiv.org/abs/2304.07193)
- Ruiz et al., **DreamBooth**：[论文](https://arxiv.org/abs/2208.12242)
- 官方代码：[facebookresearch/dino](https://github.com/facebookresearch/dino)、[facebookresearch/dinov2](https://github.com/facebookresearch/dinov2)
