# HEIM（Holistic Evaluation of Text-to-Image Models）

## 数据卡

- **任务**：文生图的整体、多方面评价框架，而非单一 prompt 文件或单一指标。
- **原版设计**：**62 个 scenarios、12 个 aspects、25 个 metrics**；网站后续 scenario/metric 数量可能扩展，需标版本。
- **12 方面**：text-image alignment、image quality、aesthetics、originality、reasoning、knowledge、bias、toxicity、fairness、robustness、multilinguality、efficiency。
- **组成**：scenario prompts、适配方式、自动指标和 crowdsourced human evaluation，公开多模型生成结果与人工结果。

## 适合用途

检查评测是否只看对齐/画质而遗漏偏见、毒性、多语言、鲁棒性和效率；复用 HELM 代码框架生成统一结果表。具体指标仍需按本资料库各类卡片固定版本。

## 局限

原版模型与场景反映 2023 年生态，直接沿用总体排名会过时；12 方面的指标量纲不同，不应任意加权成单一总分。实时网站的扩展版不能与论文 62/25 口径混写。

## 来源

- Lee et al., **Holistic Evaluation of Text-to-Image Models**, NeurIPS 2023 D&B：[论文](https://arxiv.org/abs/2311.12987)
- 官方结果：[Stanford CRFM HEIM](https://crfm.stanford.edu/heim/latest/)
- 代码：[stanford-crfm/helm](https://github.com/stanford-crfm/helm)
