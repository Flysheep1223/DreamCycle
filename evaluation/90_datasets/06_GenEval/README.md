# GenEval Prompt Set（原版）

## 数据卡

- **任务**：对象中心的组合文生图评测。
- **规模**：官方 `evaluation_metadata.jsonl` 共 **553 条**。
- **六类数量**：single_object 80、two_object 99、counting 80、colors 94、position 100、color_attr 100。
- **标注**：每条有 `prompt`、`tag` 和 `include` 中对象/数量等结构化约束；官方支持用不同 seed 生成新模板样本。

## 适合指标

[GenEval 原版](../../01_alignment/06_GenEval/) 的 Mask2Former+CLIP 检测流水线；官方生成示例为每 prompt 4 图。

## 优点与局限

结构化标签使检测规则可审计，适合数量、共现、位置和颜色归属。局限是类别/属性/模板覆盖有限，对开放实体、复杂长文本、画质、文字和知识不足。公开长期使用还会导致 benchmark drift。

## 复现必填

原始 prompts 文件还是重新采样、采样 seed、检测器权重、代码 commit、4 图是否全部计入。`% correct prompts` 的 any-of-4 与六任务 overall 不可混用。

## 来源

- 论文：[GenEval](https://arxiv.org/abs/2310.11513)
- 官方 prompt 与代码：[djghosh13/geneval](https://github.com/djghosh13/geneval)
- 后续新集：[GenEval 2](../07_GenEval2/)
