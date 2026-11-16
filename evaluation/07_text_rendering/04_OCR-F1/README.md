# OCR Precision / Recall / F1（端到端文字检测识别）

## 一句话介绍

将 OCR 预测文本区域与 GT 区域匹配，只有位置和内容都满足要求才算 TP，从而同时惩罚错字、多字、漏字和多余文本区域。

- **Precision**：OCR 输出的区域中，有多少是正确的
- **Recall**：GT 要求的区域中，有多少被正确生成并识别
- **F1**：Precision 与 Recall 的调和平均，越高越好
- **注意**：纯检测 F1 与端到端识别 F1 不同，后者还要求文字内容正确

## 匹配规则

对每个 OCR 预测与 GT，通常要求：

1. 文本框 `IoU ≥ τ`（或在无框生成任务中满足指定区域/顺序匹配）；
2. 归一化文本 exact match，或达到预设 NED 阈值；
3. 通过一对一匹配（如 Hungarian）避免一个预测对应多个 GT。

匹配成功为 TP；未匹配预测为 FP，包括多生成区域、位置不对或错字；未匹配 GT 为 FN，包括漏生成、OCR 未检出或错字（具体是否同时计 FP/FN需按协议）。

`P = TP/(TP+FP)`

`R = TP/(TP+FN)`

`F1 = 2PR/(P+R)`，分母为 0 时按预先约定处理并公开样本数。

## Detection F1 与 Recognition-aware F1

- **Detection F1**：只看文本框位置，不看字符内容；适合测“是否生成了文字区域”。
- **End-to-end F1**：位置和字符串都正确，适合视觉文字生成。
- 若 AnyText 等论文仅使用 Sentence Accuracy/NED，不要把其他论文的 OCR-F1 当同一原始指标；各基准可能采用不同匹配协议。

## 聚合方式

- **Micro**：汇总全数据集 TP/FP/FN 后再算 P/R/F1，文本多的图权重更大。
- **Macro**：每图先算 F1再平均，每张图权重相同。
- 多语言应按语言分别报告，并说明 OCR 是否共享同一模型。

## 优点

- 比只计算 GT 字符串相似度更能惩罚额外幻觉文字和漏区域。
- P/R 分解能区分“到处乱生成文字”与“大量漏字”。
- 端到端版本直接对应多文本海报/广告的实际可用性。

## 局限

- 结果对 box IoU 阈值、OCR 检测器、匹配算法和文本归一化非常敏感。
- 若生成任务没有位置要求，过严的 IoU 会惩罚内容正确但布局合理的输出；此时可改用文本集合匹配并另报布局分。
- exact match 下错一个字符即不能 TP；可辅以 NED/CER 保留部分正确信息。
- 不评价非文字区域、视觉美感或 OCR 之外的人眼可读性。

## 推荐报告

`end-to-end OCR-F1 / OCR engine & version / IoU threshold / one-to-one matching / text normalization / micro or macro`，并同时给 P、R、TP/FP/FN 数量。人工抽查一小部分，估计 OCR 本身的误检率。

## 来源与工具

- 文本检测/识别评价思想可参考 ICDAR Robust Reading Competition：[ICAR RRC](https://rrc.cvc.uab.es/)
- 常用 OCR：[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- 多区域文字基准：[TextCrafter / CVTG-2K](https://arxiv.org/abs/2503.23461)
