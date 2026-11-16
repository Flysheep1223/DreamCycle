# DreamBench

## 数据卡

- **任务**：DreamBooth 类主体驱动/个性化生成。
- **规模**：**30 个 subject、25 条 prompt**，通常组合成 750 个 subject-prompt 条件。
- **内容**：多种物体与活体主体，每个主体有参考图，prompt 要求在新场景、姿态、风格中生成。
- **标注**：参考图与 prompt，不提供唯一目标图。

## 经典评分三件套

- **DINO-I**：主体视觉保持；
- **CLIP-I**：参考图与生成图的 CLIP 图像相似；
- **CLIP-T**：生成图与目标 prompt 的文本对齐。

## 优点与局限

简单、历史可比结果多，能显示主体保持与文本遵循的权衡；但规模小、主体和风格多样性有限，整图 embedding 对身份关键细节不够敏感。可用 DreamBench++、RefVNLI 和人工评价补充。

## 来源

- Ruiz et al., **DreamBooth: Fine Tuning Text-to-Image Diffusion Models for Subject-Driven Generation**：[论文](https://arxiv.org/abs/2208.12242)
- 官方项目：[dreambooth.github.io](https://dreambooth.github.io/)
- 扩展：[DreamBench++](../27_DreamBenchPP/)
