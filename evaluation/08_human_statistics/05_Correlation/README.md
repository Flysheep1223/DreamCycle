# SRCC / PLCC / KRCC（自动指标与人评分相关性）

## 一句话介绍

用 Spearman、Pearson、Kendall 相关衡量自动分数与人工 MOS/偏好的一致性，是验证 IQA、文图对齐和偏好评分器的元评价指标，不是生成模型本身的质量分。

- **SRCC**：Spearman Rank Correlation Coefficient，单调排序相关
- **PLCC**：Pearson Linear Correlation Coefficient，线性相关
- **KRCC**：Kendall Rank Correlation Coefficient，成对 concordance
- **输出**：通常 -1 到 1；1 完全正相关，-1 完全负相关，0 无线性/单调/成对信号（依指标）

## 1. SRCC

将自动分与人工分分别转成名次，再计算名次 Pearson 相关。无 ties 时可写：

`SRCC = 1 - 6Σ_i d_i² / [n(n²-1)]`

有大量 ties 时必须使用秩相关的通用公式/成熟库，不能套用无 ties 简化式。SRCC 不要求线性，只要求同向单调，适合不同量纲的评分器。

## 2. PLCC

`PLCC = Σ_i(x_i-x̄)(y_i-ȳ) / sqrt(Σ_i(x_i-x̄)² Σ_i(y_i-ȳ)²)`

评价线性关系，对离群点和非线性敏感。IQA 文献常先对自动分做非线性 logistic 映射到 MOS，再算 PLCC/RMSE；若这样做，映射只能在训练折拟合，测试折评估，避免用测试标签拟合后虚高。

## 3. KRCC

对所有样本对判断 concordant/discordant：

- 自动分和人工分都把 A 排在 B 前：concordant；
- 一个把 A 前、另一个把 B 前：discordant。

Kendall τ-b 会处理 ties，适合小样本和强调两两排序的场合。样本量大时朴素两两计算 O(n²)，需用优化实现。

## 三种“相关性实验”不要混淆

1. **实例级点评分**：同图自动分 vs 人工 MOS，样本多但同 prompt/同模型样本不独立。
2. **实例级成对判断**：同 prompt 两图谁好，直接算成对准确率或 Kendall，通常更贴近模型选择。
3. **模型级排序**：每模型平均分 vs 人工模型平均分；模型数常很小，一两个模型就能显著改变相关系数。

论文中“与人相关更高”必须说明是哪一种。

## 优点与局限

- SRCC/KRCC 关注排序，适合模型横评；PLCC 关注数值校准，适合 MOS 回归。
- 高相关不意味着评分器能发现某类反例，也不意味着跨新模型仍稳定。
- 大量相同人工分/自动分会影响 ties；需报有效 n、模型数、prompt 数和区间。
- 只报相关不报散点图，可能掩盖非线性、离群点和分模型簇的假象。
- 若人工数据用于训练评分器，应在独立数据/模型家族上外部验证。

## 推荐报告

`SRCC / KRCC(τ-b) / PLCC` 选与目标匹配的指标，给 95% bootstrap CI（按 prompt 聚类）、有效样本数、ties 规则、是否拟合非线性映射。再补成对偏好准确率和对抗反例测试。

## 来源与实现

- Spearman/Kendall/Pearson 经典统计定义；SciPy 实现：[scipy.stats](https://docs.scipy.org/doc/scipy/reference/stats.html)
- Gecko 将 metric 验证分为模型排序、成对实例和点实例任务：[论文](https://arxiv.org/abs/2404.16820)
- AGIQA-3K 使用 SRCC/PLCC 等验证生成图质量指标：[论文](https://arxiv.org/abs/2306.04717)
