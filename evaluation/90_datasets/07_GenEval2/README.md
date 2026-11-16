# GenEval 2 Prompt Set

## 数据卡

- **任务**：更广视觉 primitive、更高组合度的文生图评测。
- **规模**：**800 条英文 prompt**。
- **字段**：`prompt`、`atom_count`、`vqa_list`、`skills`。
- **技能**：object、attribute、position、count 等；每 prompt 原子数可变，用于按 atomicity 分析。

## 适合指标

[Soft-TIFA AM/GM](../../01_alignment/07_GenEval2_SoftTIFA/)：AM 用于原子/技能估计，GM 用于 prompt 联合满足。官方也提供 VQAScore、TIFA 对照代码。

## 与原版差异

不是原版 553 条的简单扩充，也不是 Mask2Former 检测分升级版。数据、问题标注、评分器和总体聚合均变化，报告时不可只写“GenEval”而不写版本。

## 许可与复现

截至整理日官方仓库标为 **CC BY-NC 4.0**；商业使用前检查最新 LICENSE。固定 JSONL 哈希、VQA 快照、概率提取方式、AM/GM 和每 prompt 图数。

## 来源

- 论文：[GenEval 2: Addressing Benchmark Drift](https://arxiv.org/abs/2512.16853)
- 官方数据与代码：[facebookresearch/GenEval2](https://github.com/facebookresearch/GenEval2)
