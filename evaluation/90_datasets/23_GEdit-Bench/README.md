# GEdit-Bench 数据集

## 数据卡

- **任务**：真实用户需求驱动的通用图像编辑。
- **规模**：Full set **606 个实例**、11 类编辑。
- **语言**：每实例英文和中文指令各一。
- **原论文共同子集**：EN Intersection 434、CN Intersection 422；是所比较方法均有输出的交集，不是独立随机 split。
- **类别**：背景、颜色、材质、动作、人物、风格、主体增删换、文字、色调等。

## 适合指标

[GEdit SC/PQ/O](../../06_editing_multimodal/02_GEdit-Bench/)，GPT-4.1 或 Qwen2.5-VL-72B judge；也可另加背景保持和 OCR 专项。

## 关键统计坑

Full set 对每个模型仅平均成功返回的图像，拒答/失败不直接扣分。跨模型比较需同时给无输出率和各自有效样本数；Intersection 则受所选对手池影响，换模型集合后交集会变化。

## 来源

- 论文：[Step1X-Edit](https://arxiv.org/abs/2504.17761)
- 数据：[stepfun-ai/GEdit-Bench](https://huggingface.co/datasets/stepfun-ai/GEdit-Bench)
- 评分代码：[GEdit-Bench/EVAL.md](https://github.com/stepfun-ai/Step1X-Edit/blob/main/GEdit-Bench/EVAL.md)
