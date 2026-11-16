# OneIG-Bench

## 一句话介绍

一个可按需选择维度的综合文生图评测套件，将**语义对齐、文字渲染、知识推理、风格和多样性**分开评分，并提供中英文及多语言 prompt。

- **论文**：NeurIPS 2025 Datasets & Benchmarks
- **数据**：六个 prompt 集，共 1,320 条不同 prompt 定义；前五类各有中英文版本，另有多语言集
- **推荐生成**：每 prompt 4 张、不同 seed
- **不是单一公式**：各维度用不同模型/脚本，应保存并报告分项

## 六个 prompt 集

| 集合 | 数量 | 主要用途 |
|---|---:|---|
| Anime and Stylization | 245 | 动漫、艺术风格及对齐 |
| Portrait | 244 | 人物、属性与肖像生成 |
| General Object | 206 | 通用对象与主体元素对齐 |
| Text Rendering | 200 | 文字精度、完整率与文字生成 |
| Knowledge and Reasoning | 225 | 隐含知识、意图理解与逻辑合理内容 |
| Multilingualism | 200 | 多语言 prompt 与文化元素 |

前五类合计 1,120，加 Multilingualism 200 为 1,320。中英文版本是同一 benchmark 的不同语言模式，不应把翻译副本再重复计为独立 prompt 数。

## 五个评分维度

1. **Alignment**：在 General Object、Portrait、Anime/Stylization 等集合上检查 prompt 中主体元素是否被实现；中文模式还包括多语言集。
2. **Text**：文字内容的编辑距离、完全正确/完成情况等，关注拼写而不是只看海报美感。
3. **Reasoning**：判断知识/推理 prompt 所要求的生成内容是否语义与逻辑合理。
4. **Style**：对带风格标注的样本使用风格表示（官方涉及 CSD、CLIP 与 OneIG-StyleEncoder）评估风格匹配。
5. **Diversity**：对同 prompt 多 seed 输出衡量多样性；官方依赖 DreamSim、DINO 等模型。多样性必须与对齐联合看，随机错误也会产生差异。

官方脚本允许只生成并评测指定维度对应的集合，不必为某一维跑完整 1,320 条。

## 优点

- 将通用 benchmark 常混在一起的能力拆开，尤其适合诊断多语言、文字与风格。
- 同一框架包含中英文，便于检验跨语言能力而非只看英文。
- 每 prompt 多 seed 设计支持期望质量与组内多样性分析。
- 提供细粒度分析脚本和逐维度运行入口。

## 局限与复现注意

- 各维度 backbone 和量纲不同，overall 的权重/归一化必须按官方版本，不宜自行平均原始分。
- 风格相似、知识判断和 VLM judge 都有领域偏差；风格贴近不代表主体元素正确。
- 多样性高可能是输出不稳定；应同时报 alignment/text/reasoning 成功率。
- 中英文结果是不同测试模式，不应直接合并而不写语言权重。
- 官方脚本依赖多个外部模型，需冻结 checkpoint 与仓库 commit。

## 推荐使用方式

- 若只关心通用对齐，不必引用 OneIG overall；选对应子集并报告 Alignment。
- 若模型宣称文字、多语言、风格能力，OneIG 的专项维度比通用 CLIPScore 更有针对性。
- 保存四类信息：prompt ID、语言、seed、维度原始输出；按 prompt 类别宏平均并给区间。
- 与 GenEval 2/DPG-Bench 组合：前者深测组合，OneIG 补文字、风格、多语言和多样性。

## 官方来源

- Chang et al., **OneIG-Bench: Omni-dimensional Nuanced Evaluation for Image Generation**：[论文](https://arxiv.org/abs/2506.07977)
- 项目页：[oneig-bench.github.io](https://oneig-bench.github.io/)
- 官方代码：[OneIG-Bench/OneIG-Benchmark](https://github.com/OneIG-Bench/OneIG-Benchmark)
- 数据：[Hugging Face: OneIG-Bench/OneIG-Bench](https://huggingface.co/datasets/OneIG-Bench/OneIG-Bench)
