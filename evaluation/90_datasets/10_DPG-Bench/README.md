# DPG-Bench 数据集

## 数据卡

- **任务**：长、稠密 prompt 的多实体语义覆盖。
- **规模**：**1,065 条 prompt**。
- **构建**：参考 COCO、PartiPrompts、DSG-1k、Object365 等，使用 GPT-4 扩写为稠密描述并人工检查。
- **标注**：Dense Prompt Graph 问题与依赖，覆盖 Global、Entity、Attribute、Relation、Other。

## 适合指标

[DPG-Bench](../../01_alignment/09_DPG-Bench/) 的 mPLUG-large VQA 流水线，官方脚本默认 `PIC_NUM=4`。适合比较长 prompt 条件下的漏实体、错属性和错关系。

## 优点与局限

比短模板更接近复杂真实描述，依赖问题可解释；但 judge 对细粒度视觉的上限、问题覆盖和推理成本需要考虑。它不提供感知质量或人工偏好真值。

## 复现必填

`prompt与graph版本 / mPLUG checkpoint / PIC_NUM / resolution / 五分项 / overall聚合 / 是否prompt rewrite`。

## 来源

- ELLA 论文：[arXiv 2403.05135](https://arxiv.org/abs/2403.05135)
- 官方数据与 `dpg_bench` 代码：[TencentQQGYLab/ELLA](https://github.com/TencentQQGYLab/ELLA)
