# T2I-CompBench++ 数据集

## 数据卡

- **任务**：开放世界组合文生图。
- **规模**：**8,000 条 prompt**；原版 T2I-CompBench 为 6,000。
- **四大类**：attribute binding、object relationships、generative numeracy、complex compositions。
- **八子类**：color、shape、texture binding，2D/3D spatial，non-spatial，numeracy，complex。

## 标注与评分对应

属性文本配 BLIP-VQA 问题；空间/数量配 UniDet 检测规则，3D 结合深度；非空间与复杂组合按原版或 ++ 采用 CLIP、3-in-1 或 MLLM。不同子集并不是同一评分公式。

## 适合指标

[T2I-CompBench++ 官方套件](../../01_alignment/08_T2I-CompBench/)，也可作为 Soft-TIFA/VQAScore 的外部组合测试，但需重新生成原子问题，不能直接沿用原表。

## 版本坑

原版与 ++ 的 prompt、评分器和每 prompt 图数不同；官方历史代码有 10 图/prompt 的实验设置。报告必须写子类、生成数量和 macro 规则，不能只写“CompBench score”。

## 来源

- 原版：[NeurIPS 2023 论文](https://arxiv.org/abs/2307.06350)
- ++：[TPAMI 2025 DOI](https://doi.org/10.1109/TPAMI.2025.3531907)
- 官方数据与代码入口：[Karine-Huang/T2I-CompBench](https://github.com/Karine-Huang/T2I-CompBench)
