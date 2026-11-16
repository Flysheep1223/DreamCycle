# DrawBench

## 数据卡

- **任务**：通用文生图人工/自动评价。
- **规模**：**200 条英文 prompt**。
- **内容**：由 Imagen 工作发布，刻意覆盖颜色、数量、空间位置、罕见词、冲突描述、长描述、文字和来自 Reddit 等复杂情况。
- **形式**：prompt 列表；不是带唯一目标图的配对数据集。

## 适合指标

人工 side-by-side/MOS、HPS benchmark、CLIPScore、VQAScore、TIFA/VIEScore。TIFA-160 是从相关数据构建的常用人工相关子集，但 TIFA v1.0 与 DrawBench 不是同一规模，不能混写。

## 优点与局限

规模小、挑战类型多样，适合定性案例与多模型人工评审；但仅 200 条，模型级均值的区间可能较宽，且公开使用多年，易被训练/调参间接覆盖。不能凭少数精选 DrawBench 图代表完整模型能力。

## 推荐协议

公开全部 200 条结果或预先固定抽样；每 prompt 多 seed；人工比较隐藏模型名并随机左右。自动分报告 prompt 宏平均和区间。

## 来源

- Saharia et al., **Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding (Imagen)**：[论文](https://arxiv.org/abs/2205.11487)
- 官方代码/数据目录：[google-research/drawbench](https://github.com/google-research/google-research/tree/master/drawbench)
