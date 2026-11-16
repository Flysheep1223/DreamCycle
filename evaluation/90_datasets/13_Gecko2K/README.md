# Gecko2K

## 数据卡

- **任务**：技能覆盖均衡的文生图评价与评分器元评价。
- **规模**：约 **2,000 条 prompt**，以及约 **100k 人工标注**，覆盖 4 个 T2I 模型与 4 种人工标注模板。
- **子集**：Gecko(S) 为按技能/子技能系统构建；Gecko(R) 为扩展 DSG1k 思路的重采样真实/多样化 prompt。
- **技能**：命名实体、文字、语言复杂度、动作/空间/尺度关系，以及颜色、数量、表面、形状、风格等属性。

## 三种元评价任务

1. 模型整体排序；2. 实例级成对评分；3. 实例级点评分。自动指标应在三种任务上分别验证，而不是只报一个平均 SRCC。

## 适合指标

Gecko 的可解释 QA/VQA 方法、TIFA、DSG、VQAScore、CLIPScore 等。人工数据用于验证人机一致性，不应直接当生成图训练集。

## 核心启示

只在一个 prompt slice、技能或人工模板上验证，指标排名可能不稳定；新模型上还需重新检查 benchmark drift。

## 来源

- Wiles et al., **Revisiting Text-to-Image Evaluation with Gecko**, ICLR 2025：[论文](https://arxiv.org/abs/2404.16820)
- 官方代码与数据：[google-deepmind/gecko_benchmark_t2i](https://github.com/google-deepmind/gecko_benchmark_t2i)
