# DSG（Davidsonian Scene Graph）

## 一句话介绍

把 prompt 组织成由**唯一、原子语义问题及依赖边**构成的图，再用 VQA 回答；若父级对象/前提不存在，依赖它的子问题不得“凭空答对”，从而提高细粒度评测的一致性。

- **输入**：prompt、预生成的 DSG 问题/依赖图、生成图
- **输出**：0–1 或百分比，越高越好
- **原始组成**：LLM 问题生成 + VQA 回答；可模块化替换
- **数据**：DSG-1k，官方实际为 **1,060 条 prompt**

## 为什么需要依赖图

普通独立 QA 可能出现：对“没有摩托车”的图，VQA 仍回答“摩托车是蓝色”。DSG 让“摩托车颜色”依赖于“存在摩托车”，父问题为否时将子问题置 0，避免相互矛盾的答案抬高分数。

## 评分流程

1. LLM 从文本生成原子语义 tuples。
2. 为 tuples 标注 parent/dependency，形成有向依赖图。
3. 将 tuple 转成自然语言 yes/no 问题。
4. VQA 对生成图逐题回答，答 Yes 记 1、No 记 0。
5. 若任一父问题为 0，将相应子问题置 0。
6. 对有效问题及数据集求均值，并按类别报告。

官方伪代码的核心为：

`score_q = 1[VQA(x,q)="yes"]`

`score_q ← 0, 若 score_parent=0`

`DSG_image = mean_q(score_q)`

## DSG-1k 数据

官方脚本给出的 8 类与数量为：TIFA 160、paragraph 200、relation 100、count 100、real_user 200、pose 100、defying 100、text 100，共 **1,060**。官方发布了用 PaLM 2 生成的问题，便于不必重建 QG 的复现。

该集覆盖长段落、真实用户文本、关系、计数、动作姿态、反常场景与文字。它仍不是全能力基准；画质和偏好需另测。

## 优点

- 原子且去重的问题提高语义覆盖，依赖关系抑制不合理得分。
- 可以输出问题级失败，便于诊断对象、属性、关系等薄弱点。
- QG/VQA 模块可替换；官方提供 mPLUG-large、InstructBLIP 等历史接口及示例。
- 原始论文在 TIFA-160 人工相关实验中展示了比朴素 QG/A 更可靠的细粒度评价。

## 局限

- 依赖 LLM 的 tuple、依赖边和问题质量；错误图结构会系统性漏评或误评。
- 多数问题二值化，丢失“部分满足”和回答不确定性；可借鉴 Soft-TIFA 改用概率，但那就不是原始 DSG 分数。
- VQA 对数量、空间、视觉文字仍有上限，judge 错误会沿依赖边传播。
- 逐图多问题，成本高于单次 CLIPScore/VQAScore。
- 换 judge 或问题版本后分数不可直接复用。

## 推荐报告

分别给总体、8 类分项、有效问题数、VQA 模型、问题文件版本、父级归零规则和 prompt 宏/微平均。人工抽查时区分：QG 错误、依赖错误、VQA 错误、真实生成错误。

## 官方来源与代码

- Cho et al., **Davidsonian Scene Graph: Improving Reliability in Fine-grained Evaluation for Text-to-Image Generation**, ICLR 2024：[论文](https://arxiv.org/abs/2310.18235)
- 项目页：[google.github.io/dsg](https://google.github.io/dsg/)
- 官方代码、DSG-1k 问题与计分脚本：[j-min/DSG](https://github.com/j-min/DSG)

> DSG-1k 的“1k”是名称，不应四舍五入写成 1,000；官方明确为 1,060。
