# 标注一致性：Agreement、Cohen/Fleiss κ、Krippendorff α、Kendall W、ICC

## 一句话介绍

衡量不同标注者对同一图像/比较是否给出一致判断，用于区分“信号稳定”与“个人口味差异”；它不是人机相关性，也不证明标注本身正确。

- **输入**：同一批样本的多标注者原始标签或排序
- **输出**：依指标而异，通常越接近 1 越一致，0 附近可能接近随机
- **选择依据**：类别/有序/连续、两/多标注者、是否有缺失、是否排名

## 1. Percent Agreement

`Agreement = 一致标注数 / 总标注数`

简单直观，但类别不平衡时，全部选多数类也会很高，不能单独作为可靠性证据。

## 2. Cohen's κ（两名标注者、类别标签）

`κ = (p_o-p_e)/(1-p_e)`

`p_o` 为观察一致率，`p_e` 为按双方边缘分布得到的随机一致率。适合名义类别；有序评分可用加权 κ，权重需声明。类别极不平衡时 κ 的“paradox”需结合原始列联表看。

## 3. Fleiss' κ

将机会校正 κ 扩展到多名标注者、固定数量评分的名义类别。若每个样本标注者不完全相同或有缺失，Krippendorff α 往往更灵活。

## 4. Krippendorff's α

通用形式：

`α = 1 - D_observed / D_expected`

可按 nominal、ordinal、interval、ratio 等定义距离，支持多标注者与缺失数据。 ordinal 距离适合 Likert 有序评分。α 高表示可重复性较好，但可接受阈值依赖用途和风险，不能机械套一个通用 cutoff。

## 5. Kendall's W

用于多名标注者对同一组对象给出完整排名时的一致性，0 到 1，越高越一致。少量成对比较或不完整排序需用适配方法，不应强行补齐。

## 6. ICC（Intraclass Correlation）

适合连续/近似连续评分，用于评估评分者间绝对一致或一致性。ICC 有一致性/绝对一致、单次/平均测量等不同形式，报告必须写型号，例如 `ICC(A,1)`，不能只写 ICC=0.7。

## 如何选择

| 数据 | 推荐 |
|---|---|
| 两人 A/B/tie | Percent agreement + Cohen κ + 混淆矩阵 |
| 多人 A/B/tie、可有缺失 | Krippendorff α（nominal） |
| 多人 1–5 Likert | Weighted κ（两人）或 ordinal α；可补 ICC |
| 多人完整模型排序 | Kendall W |
| 连续 MOS 原始分 | 明确型号的 ICC + 分布/方差 |

## 使用建议

- 先发布 rubric 和 pilot 结果，再冻结正式标注。
- 一致性低时检查题意、图像加载、标注者培训和任务本身主观性，不要简单删除少数意见。
- 同时保留逐标注者数据，方便分层分析文化、专业背景与偏好差异。
- 自动评审器与人的一致性是另一问题：应另算成对准确率、SRCC 等，不能把人际 α 当人机 α。

## 参考

- Cohen, **A Coefficient of Agreement for Nominal Scales**, 1960
- Krippendorff, **Content Analysis: An Introduction to Its Methodology**
- Kendall & Babington Smith, **The Problem of m Rankings**, 1939
- GenAI-Bench 报告图像/视频对齐标注的 Krippendorff α 示例：[论文](https://arxiv.org/abs/2406.13743)
- Python 实现：[krippendorff](https://github.com/pln-fing-udelar/fast-krippendorff)、[pingouin ICC](https://pingouin-stats.org/)
