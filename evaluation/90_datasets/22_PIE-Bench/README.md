# PIE-Bench 数据集

## 数据卡

- **任务**：prompt/inversion 图像编辑。
- **规模**：**700 张图、10 类编辑**。
- **场景**：animal、human、indoor、outdoor，含自然与人工图像。
- **每条五项标注**：source prompt、target prompt、editing instruction、编辑主体、人工编辑 mask。

## 适合指标

[PIE-Bench 官方套件](../../06_editing_multimodal/01_PIE-Bench/)：Structure Distance、mask 外 PSNR/SSIM/MSE/LPIPS、全图/编辑区 CLIP、推理时间。也可算 Directional CLIP，但应标为扩展。

## 优点与局限

人工 mask 使“该改哪里、哪里应保持”可审计，适合局部编辑。局限是规模和指令风格较受控，对真实开放指令、多轮、多参考、复杂文字不足。不同论文过滤后的有效样本数可能不同，应公布列表。

## 来源

- 论文：[Direct/PnP Inversion](https://arxiv.org/abs/2310.01506)
- 官方项目与数据入口：[cure-lab.github.io/PnPInversion](https://cure-lab.github.io/PnPInversion/)
- 官方代码：[cure-lab/PnPInversion](https://github.com/cure-lab/PnPInversion)
