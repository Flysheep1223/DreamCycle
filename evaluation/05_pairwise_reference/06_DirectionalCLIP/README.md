# Directional CLIP Similarity / CLIP Direction Loss

## 一句话介绍

比较“源图→生成图”的 CLIP 图像变化方向与“源文本→目标文本”的 CLIP 文本变化方向是否一致，专门评价编辑是否朝指定语义方向发生，而非只看目标图整体像不像 prompt。

- **输入**：源图、编辑后图、源描述、目标描述
- **输出**：方向 cosine，越高越好
- **适用**：文本引导编辑、风格/属性变化
- **前提**：需要可靠的源文本和目标文本，不只是单条模糊编辑指令

## 公式

`ΔI = E_I(x_edit) - E_I(x_source)`

`ΔT = E_T(c_target) - E_T(c_source)`

`S_direction = cos(ΔI, ΔT)`

作为训练损失时常写 `L_direction = 1 - S_direction`；作为评测分数时报告 cosine，方向不要写反。

## 与 CLIPScore 的差别

CLIPScore 只看编辑图与目标文本是否接近；Directional CLIP 还显式考虑源状态。例如“戴帽子的狗→戴红色帽子的狗”与“没戴帽子的狗→戴红色帽子的狗”目标文本相同，但应有不同的变化方向。

## 优点

- 直接建模编辑语义变化，比全图 CLIP-I 更不容易只奖励保持。
- 不需要像素对齐或唯一目标图。
- 可微，既可用于训练也可用于诊断编辑方向。

## 局限

- 方向相似不保证未编辑区域保持，也不保证图像质量。
- 源/目标 caption 写法会改变 `ΔT`；使用简短编辑指令代替源—目标对时并非原始定义。
- CLIP 对数量、否定、复杂关系和文字的盲区仍然存在。
- 原图与编辑图完全相同会使 `ΔI≈0`，cosine 数值不稳定，应检测零范数并单独处理。
- 不同 CLIP 权重和文本模板不可直接比较。

## 推荐搭配

与 masked background PSNR/LPIPS、指令成功率/VIEScore 和感知质量联合。最好同时报告目标 CLIP-T 与方向分：方向对但目标未完成、目标像但变化方向错，都可能发生。

## 来源

- Patashnik et al., **StyleCLIP: Text-Driven Manipulation of StyleGAN Imagery**, ICCV 2021（directional CLIP loss）：[论文](https://arxiv.org/abs/2103.17249)
- Gal et al., **StyleGAN-NADA: CLIP-Guided Domain Adaptation of Image Generators**：[论文](https://arxiv.org/abs/2108.00946)
- CLIP 官方代码：[openai/CLIP](https://github.com/openai/CLIP)
