# Q-Align / OneAlign

## 一句话介绍

把图像质量/美学评分教成大模型的离散语言分类，让它在 excellent、good、fair、poor、bad 五级上输出概率，再加权成连续分。

- **输入**：单图与质量或美学问题
- **原始输出等级**：excellent / good / fair / poor / bad
- **原始连续分**：1–5，越高越好
- **OneAlign**：合并质量与美学等能力的后续统一模型；应标明具体模型而非统称 Q-Align

## 原始计算

模型在回答位置对五个等级词的 log-prob/logits 做 softmax：

`p_i = exp(l_i) / Σ_j exp(l_j)`

再计算：

`Q-Align = 5*p_excellent + 4*p_good + 3*p_fair + 2*p_poor + 1*p_bad`

相比只取概率最大的等级，加权平均保留模型不确定性，使分数更连续。这个 1–5 不是人工 MOS 的直接百分比，仍需在目标域校准。

## 质量与美学分开提问

- IQA 示例：询问图片 quality，关注失真、清晰度、视觉缺陷。
- IAA 示例：询问 aesthetics，关注构图、色彩与艺术吸引力。
- 文图对齐不是原始 Q-Align 的自动能力；需用专门 alignment 数据训练的后续模型或 VQAScore 等。

后续 Q-Align 家族、OneAlign 或其他衍生版本可能使用不同 backbone、等级权重甚至 0–1 归一化，必须记录模型 ID 和评分函数，不能沿用原始 1–5 表头。

## 优点

- 用语言等级把 MOS 监督转成 LMM 易学习的分类任务，兼顾视觉理解和评分。
- 概率加权比硬分类更细，模型也有潜力提供自然语言解释。
- 同一架构可适配 IQA、IAA 等任务，并可在下游数据微调。
- 相比简单 CLIP 反义提示，更适合利用大规模多模态模型能力。

## 局限

- 推理成本高于 CLIP/MUSIQ，且受模型版本、prompt、图像分辨率影响。
- 训练数据仍以视觉质量/美学为主，不保证识别所有生成式结构错误、漏字或语义不符。
- 语言 token 概率存在校准问题，五个等级的分布不一定等于人的 MOS 分布。
- Q-Align、OneAlign 及后续重训版本的分值范围可能不同；跨模型排名原始分不合理。
- 不应把自然语言解释当作已验证的错误定位证据，仍需人工抽查。

## 推荐报告

写明 `model_id / revision / task=quality|aesthetic / prompt / level weights / 输入分辨率`，并报告在 AGIQA-3K 等目标域人工标注上的 SRCC、PLCC。若只需快速回归，可固定同一 checkpoint，比较相对变化而非绝对等级。

## 官方来源

- Wu et al., **Q-Align: Teaching LMMs for Visual Scoring via Discrete Text-Defined Levels**, ICML 2024：[论文](https://arxiv.org/abs/2312.17090)
- 项目页：[q-future.github.io/Q-Align](https://q-future.github.io/Q-Align/)
- 官方组织与模型：[Q-Future](https://github.com/Q-Future)
- PyTorch IQA 集成：[IQA-PyTorch](https://github.com/chaofengc/IQA-PyTorch)
