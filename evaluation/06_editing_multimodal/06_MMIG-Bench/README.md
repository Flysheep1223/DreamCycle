# MMIG-Bench 与 AMS（Aspect Matching Score）

## 一句话介绍

统一评测纯文本与“文本+参考图”条件生成，将低层身份/伪影、中层细粒度语义 AMS、高层美学/偏好放在同一框架，并提供多视角、多主体参考数据。

- **数据**：4,850 条富标注 prompt、1,750 张多视角参考图、380 个 subject
- **主体**：人物、动物、物体、艺术风格
- **人工验证**：约 32.4k 个人类评分
- **论文**：NeurIPS 2025 Datasets & Benchmarks

## 三层评价

### Low-level

- **CLIP-Text**：生成图与 prompt 的整体语义；
- **CLIP-Image、DINOv2、CUTE**：参考主体身份保持；
- **PAL4VST**：用分割模型估计生成伪影，方向按官方为越低越好。

### Mid-level：AMS

从 prompt 提取 `n` 个 aspect phrases，为每个 aspect 预生成 QA。使用 **Qwen2.5-VL-72B** 看生成图回答，与标准答案比较：

`AMS(I,P) = (1/n) Σ_i 1[predicted_answer_i = gold_answer_i]`

输出正确问题比例，常以百分数展示。问题覆盖 object、attribute、relation、counting 等语义方面，可定位具体失败。

### High-level

Aesthetic、HPS v2、PickScore 等美学/人类偏好指标。低、中、高层保留分项，不能把 AMS 当成整套 benchmark 的唯一总分。

## 优点

- 同时覆盖 T2I 与多模态条件输入，补足“定制生成只测身份、不测复杂语义”的缺口。
- 多视角参考与多类主体可检验跨视角保持和主体串换。
- AMS 问题级可解释，低层和高层指标提供互补证据。
- 人工评分用于验证自动指标与属性、关系、计数、对象、整体遵循的人类判断相关性。

## 局限

- AMS 依赖问题覆盖和 Qwen2.5-VL-72B 的答案准确性；自由答案 exact match 需明确同义词/格式归一化。
- 高层奖励模型本身不一定适配所有多模态主体任务，不能覆盖 CP/PF 的完整权衡。
- CLIP-I/DINOv2 仍可能受背景影响，应结合主体裁剪或人工检查。
- 多指标、多模型推理成本高，必须冻结全部 checkpoint 与 prompt 版本。
- 人物身份评价涉及数据许可与隐私，使用参考图时需遵守数据卡。

## 推荐报告

分别给 Text-only 与 Image+Text 条件；低层、AMS、高层分表；AMS 按 aspect 分项；多主体给遗漏/串换率。不要用 AMS 的高低代替感知质量，也不要只用 CLIP-I 宣称主体保持。

## 官方来源

- Hua et al., **MMIG-Bench: Towards Comprehensive and Explainable Evaluation of Multi-Modal Image Generation Models**：[论文](https://arxiv.org/abs/2505.19415)
- 项目页：[hanghuacs.github.io/MMIG-Bench](https://hanghuacs.github.io/MMIG-Bench/)
- 官方代码：[hanghuacs/MMIG-Bench](https://github.com/hanghuacs/MMIG-Bench)
- 数据：[hhua2/MMIG-Bench](https://huggingface.co/datasets/hhua2/MMIG-Bench)
