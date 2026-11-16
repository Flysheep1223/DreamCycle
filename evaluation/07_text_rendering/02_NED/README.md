# NED（Normalized Edit Distance，文字相似度版本）

## 一句话介绍

将 OCR 预测与目标文本的 Levenshtein 编辑距离按长度归一化，衡量部分正确程度；AnyText 等常用 `1−归一化距离`，所以越高越好。

> 有些领域把 NED 定义为归一化距离本身（越低越好）。必须写出公式，不能只看指标名。

- **输入**：OCR 文本与 GT 字符串
- **本卡采用**：`NED_similarity∈[0,1]`，1 为完全一致，越高越好
- **适用**：海报、场景文字、多语言生成，补充完全正确率的部分信用

## 公式

Levenshtein 距离 `d(a,b)` 是将 `a` 变成 `b` 所需的最少字符插入、删除、替换次数：

`NED_sim = 1 - d(pred,gt) / max(len(pred),len(gt))`

约定：

- 两字符串均为空：`NED_sim=1`（若该样本应纳入）；
- 一个为空、另一个非空：`NED_sim=0`；
- 长度按 Unicode 字符、字节、子词还是词计算必须声明。中英文视觉文字常用字符级，英文也可另报词级。

## 示例

GT 为 `ABCDE`，OCR 为 `ABXDE`：一次替换，长度均 5，则 `NED_sim=1-1/5=0.8`，但 Sentence Accuracy=0。

若 OCR 漏掉整句，预测为空，GT 非空，NED=0；这比简单忽略未检出样本更合理。**不要只保留 OCR 有输出的样本再平均**，否则会抬高分数。

## 聚合

- **宏平均**：先算每个文本区域/图的 NED，再平均，短文本与长文本权重相同。
- **微平均**：汇总所有编辑操作和长度后计算，长文本权重更大。
- 多区域图像可先在图内平均，再跨图平均；与直接拼接所有文本的结果不同。

## 优点

- 错一个字符和整句错误有不同惩罚，比完全正确率更细腻。
- 有界且直观，适合比较多语言、多长度文本。
- 与 OCR Accuracy 联合可区分“大量轻微错”与“少数严重错”。

## 局限

- 仍依赖 OCR、文本归一化和区域匹配；不能独立证明人眼可读。
- 字符替换、插入、删除等权，但业务上一个关键数字/名字错误可能更严重。
- 与 CER 的分母不同，不能直接互换；也不能跨字符级和词级比较。
- 高 NED 不保证所有文本区域都找到，也不惩罚额外幻觉文字，需配合 OCR-F1。

## 来源

- Levenshtein, **Binary Codes Capable of Correcting Deletions, Insertions, and Reversals**（编辑距离基础）
- Tuo et al., **AnyText**（Sentence Accuracy 与 NED 评测）：[论文](https://arxiv.org/abs/2311.03054)
- 官方 AnyText 实现与 benchmark：[tyxsspa/AnyText](https://github.com/tyxsspa/AnyText)
