# Improved Precision & Recall（分布保真与覆盖）

## 一句话介绍

在特征空间用 k 近邻球构造真实/生成分布的“流形”，分别计算生成样本落在真实流形内的比例（Precision）与真实样本被生成流形覆盖的比例（Recall）。

> 这不是图像分类的 precision/recall，也不需要逐图标签。

- **Precision↑**：生成样本更常落在真实数据附近，常解释为保真/真实性。
- **Recall↑**：真实分布的更多模式被生成集覆盖，常解释为多样性/覆盖。
- **输入**：两个足够大的图像集合及同一特征提取器
- **输出**：各为 0–1

## kNN 流形定义

对真实特征 `x_i`，计算它在真实集合内到第 k 个近邻的距离 `r_i`，构造球 `B(x_i,r_i)`。真实流形近似为所有球的并集；生成流形同理。

`Precision = (1/N_g) Σ_y 1[y 落在至少一个真实邻域球内]`

`Recall = (1/N_r) Σ_x 1[x 落在至少一个生成邻域球内]`

Improved Precision and Recall 的常见设置为 `k=3`，但必须记录实现、特征和样本数。

## 如何解读组合

| Precision | Recall | 可能情况 |
|---|---|---|
| 高 | 低 | 输出真实但模式覆盖不足/单一 |
| 低 | 高 | 覆盖广，但夹杂许多不真实或离群输出 |
| 高 | 高 | 在该特征空间与 k 设置下保真和覆盖都好 |
| 低 | 低 | 分布明显不匹配，或参考域/预处理不适合 |

这些只是诊断方向，不是唯一因果解释；两个模型分数接近也不能证明分布相同。

## 优点

- 将 FID 的一个距离拆成保真与覆盖两个轴，便于发现模式坍缩。
- 不需要 prompt 或逐图标签，可用于无参考人工评分的集合分析。
- 可换用 Inception、CLIP 或 DINOv2 特征做灵敏度分析。

## 局限

- kNN 球在高维空间对离群点、k、样本量和密度非常敏感。
- “Precision 高”不等于 prompt 对齐，“Recall 高”也不等于每个 prompt 都能多样生成。
- 真实集中的离群样本会扩大流形，可能让不真实生成也被判为高 precision。
- 特征空间决定可见的多样性；像素不同但语义相同、或语义不同但像素接近都可能被误判。
- 后续研究指出 kNN 估计对分布变化与异常点仍可能不可靠，必要时应比较概率式 PR 等改进方法。

## 推荐实践

- 固定 `N_r=N_g` 或明确不平衡样本数，重复子采样并给区间。
- 同报 Precision 与 Recall，不能只挑有利的一项。
- 用 Inception 与 CLIP/DINOv2 特征做对照；与 FID/CMMD 及人工评价联合。
- 文生图的“同 prompt 多样性”另做组内分析，不能由全局 Recall 替代。

## 来源与实现

- Kynkäänniemi et al., **Improved Precision and Recall Metric for Assessing Generative Models**, NeurIPS 2019：[论文](https://arxiv.org/abs/1904.06991)
- 早期 Precision/Recall 定义：Sajjadi et al., **Assessing Generative Models via Precision and Recall**, NeurIPS 2018：[论文](https://arxiv.org/abs/1806.00035)
- 常用实现：[clovaai/generative-evaluation-prdc](https://github.com/clovaai/generative-evaluation-prdc)、[torch-fidelity](https://github.com/toshas/torch-fidelity)
- 概率式改进分析：[Probabilistic Precision and Recall](https://arxiv.org/abs/2309.01590)
