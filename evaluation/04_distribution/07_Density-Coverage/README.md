# Density & Coverage（D&C）

## 一句话介绍

Density 统计生成样本平均落入多少个真实样本的 kNN 邻域，Coverage 统计有多少真实样本的邻域至少被一个生成样本覆盖；用于补充 Precision/Recall 对离群点和重复样本不敏感的问题。

- **Density**：通常越高表示生成点更集中在真实数据高密度区域；**可大于 1**，不是比例。
- **Coverage**：0–1，越高表示真实流形覆盖更完整。
- **输入**：两个图像集合、特征提取器与近邻参数 k

## 直观定义

先对每个真实特征 `x_i` 找其在真实集合中的第 k 近邻距离，形成邻域球 `B_i`。

- 对每个生成点 `y`，统计它落入哪些 `B_i`。Density 是这些计数的归一化平均（官方公式含 k 归一化），所以同一生成点可被多个真实邻域重复计数。
- 对每个真实点 `x_i`，只要至少一个生成点落入 `B_i`，该真实点即被覆盖；Coverage 为被覆盖真实点比例。

## 与 Precision/Recall 的差别

- Precision 只问生成点是否落入真实流形，落入 1 个或 100 个邻域都一样；Density 会区分真实区域密度。
- Recall 可能受生成离群点形成的巨大邻域影响；Coverage 只从真实样本邻域出发，降低这种影响。
- Density 对重复生成点更敏感：如果大量生成点堆在少数真实邻域，数值可能很高，但这**不表示多样性好**，必须和 Coverage 一起看。

## 优点

- Coverage 对生成离群点更稳健，直接衡量真实数据覆盖。
- Density 能区分“刚好落入真实流形”和“位于多个真实样本共同的高密度区域”。
- 与 PR 共用特征管线，便于多角度诊断。

## 局限

- 高 Density 可能奖励集中在常见模式，不能单独优化。
- 仍受 k、样本数、特征空间、参考域与异常真实样本影响。
- 不使用 prompt，不测文本对齐，也不等于用户感知多样性。
- Density 无量纲但不以 1 为上界，不能当百分比或与 Recall/Coverage 直接平均。
- 具体实现的 kNN 排除自身、距离 ties 和归一化需固定。

## 推荐报告

同时给 `Precision / Recall / Density / Coverage` 四项、特征 backbone、k、N 和子采样区间。若只关心覆盖，Coverage 通常比全局 Recall 更易解释；若关心产品多样性，仍需同 prompt 组内 Vendi/LPIPS 和语义有效性约束。

## 来源与实现

- Naeem et al., **Reliable Fidelity and Diversity Metrics for Generative Models**, ICML 2020：[论文](https://arxiv.org/abs/2002.09797)
- 官方/常用 PRDC 实现：[clovaai/generative-evaluation-prdc](https://github.com/clovaai/generative-evaluation-prdc)
- 后续稳健性讨论：[Probabilistic Precision and Recall](https://arxiv.org/abs/2309.01590)
