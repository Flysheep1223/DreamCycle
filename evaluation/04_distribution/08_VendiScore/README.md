# Vendi Score（VS）

## 一句话介绍

将一组样本的成对相似度矩阵归一化，取其特征值熵的指数，得到“有效不同元素数量”；无需真实参考集，可用于图像生成多样性分析。

- **输入**：样本集合 + 对称、半正定且自相似为 1 的相似度函数/矩阵
- **输出**：通常在 1 到 N 之间，越高表示有效多样性越大
- **解释**：N 个完全相同样本约等于 1；N 个彼此不相似样本约等于 N
- **关键依赖**：相似度核与特征提取器

## 公式

给定 `n×n` 半正定相似度矩阵 `K`，令 `K/n` 的特征值为 `λ_i`，且 `Σλ_i=1`：

`VS(K) = exp(-Σ_i λ_i log λ_i)`

其中 `0 log 0 = 0`。这也是 `K/n` 的 von Neumann 熵的指数，或称有效秩。

扩展的 order-q Vendi Score 可调整对常见元素的强调；默认常为 q=1，报告时不要混用不同 q。

## 文生图中的两种统计单位

1. **同 prompt 多 seed 组内 VS**：回答“同一条件下输出是否多样”。先对每个 prompt 的 K 张图算 VS，再跨 prompt 平均。
2. **整个测试集 VS**：回答“整集有多少有效不同图像”，但不同 prompt 本来就不同，会天然抬高 VS，不能证明每个 prompt 的采样多样性。

若 K 较小，VS 上界也小；不同 K 的原始 VS 不宜直接比较，可同时报告 `VS/K`，但归一化后解释会改变。

## 优点

- 不需要真实参考集，直接给出有效不同样本数，解释直观。
- 可使用 CLIP、DINO、DreamSim、Inception 或领域自定义相似度。
- 不只统计两两平均距离，还利用整个相似度谱，能区分不同冗余结构。
- 对图像、文本和其他模态通用。

## 局限

- **高多样性可能来自随机错误**：语义不符、伪影和噪声都能提高 VS，必须与对齐/质量联合。
- 换相似度函数就是换“不同”的定义；CLIP VS 与 pixel VS 不可直接比较。
- 直接构造 `n×n` 矩阵在大 N 下成本高，低秩 embedding 可用 dual/covariance 形式加速。
- 样本数 K 与分组方式影响结果；不可将不同 prompt 混算后声称组内多样性。
- 不需要真实分布，因此无法判断是否覆盖真实数据中“有意义”的变化。

## 推荐报告

`Vendi Score(q=1) / similarity backbone & kernel / K images per prompt / mean within-prompt VS`，同时给语义成功率和质量分。可另报组内平均 LPIPS/DreamSim 距离作为互补，但不要把不同量纲相加。

## 官方来源与实现

- Friedman & Dieng, **The Vendi Score: A Diversity Evaluation Metric for Machine Learning**, TMLR 2023：[论文](https://arxiv.org/abs/2210.02410)
- Pasarkar & Dieng, **Cousins of the Vendi Score**：[论文](https://arxiv.org/abs/2310.12952)
- 官方代码：[vertaix/Vendi-Score](https://github.com/vertaix/Vendi-Score)

```python
from vendi_score import vendi
score = vendi.score_K(similarity_matrix, q=1.0)
```
