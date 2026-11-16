# OneIG-Bench 数据集

## 数据卡

- **任务**：多维文生图，含对齐、文字、推理、风格、多样性和多语言。
- **六集**：Anime/Stylization 245、Portrait 244、General Object 206、Text Rendering 200、Knowledge & Reasoning 225、Multilingualism 200。
- **规模口径**：共 **1,320 条**；前五集提供中英文版本，Multilingualism 单独设计。
- **推荐生成**：每 prompt 4 张不同 seed 图。

## 适合指标

[OneIG-Bench 官方评分](../../01_alignment/11_OneIG-Bench/) 可按维度单独运行；文字可另用 OCR Accuracy/NED/CER，多样性可另用 Vendi，但需标明不是官方原公式。

## 优点与局限

中英文与多语言、人物、文字、风格和推理在同一框架，便于专项诊断。不同维度 backbone 与量纲不同，不应自行平均；中英文副本不能重复算独立 prompt，风格/多样性高也不代表语义正确。

## 来源

- 论文：[OneIG-Bench](https://arxiv.org/abs/2506.07977)
- 官方代码：[OneIG-Bench/OneIG-Benchmark](https://github.com/OneIG-Bench/OneIG-Benchmark)
- 数据：[HF OneIG-Bench](https://huggingface.co/datasets/OneIG-Bench/OneIG-Bench)
