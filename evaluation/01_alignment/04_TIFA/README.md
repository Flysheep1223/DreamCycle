# TIFA（Text-to-Image Faithfulness Evaluation with Question Answering）

## 一句话介绍

从 prompt 自动生成带标准答案的问题，再让 VQA 模型看生成图回答，以答案正确率评估细粒度、可解释的图文忠实度。

- **输入**：文本、文本对应的 QA 集、生成图
- **输出**：问题正确率，通常 0–1 或 0–100，越高越好
- **原始推荐 VQA**：mPLUG-large
- **数据**：TIFA v1.0 约 4,000 条文本、约 2.5 万个预生成 QA；TIFA-160 为常用于人工相关分析的子集

## 评分流程

1. **QG**：用 LLM 将 prompt 分解为对象、属性、颜色、形状、数量、空间关系等问题及参考答案。
2. **过滤**：原始方法使用 UnifiedQA 等模块检查问题与文本的一致性。
3. **VQA**：对生成图逐题提问，获得自由答案或多选答案。
4. **匹配**：将 VQA 答案与该题标准答案比较，正确记 1，否则 0。
5. **聚合**：对该图问题取平均，再对 prompt/数据集取平均。

若第 `i` 张图有 `Q_i` 个问题：

`TIFA_i = (1/Q_i) * Σ_j correct(answer_ij, gold_ij)`

必须说明所有问题直接微平均还是先对 prompt 宏平均；两种权重不同。

## 数据构成与使用

TIFA v1.0 汇集多种来源的文本，覆盖常见描述及更具挑战性的组合。官方已提供预生成问题，因此跑官方 benchmark **不需要再调用 OpenAI API**；更换 LLM 重新生成问题会形成不同版本。

TIFA-160 常用于自动指标与人工 1–5 级忠实度标注的相关性验证。DSG 官方还发布了每图 5 份 Likert 标注的扩展版本，便于复核人机一致性。

## 优点

- **可解释**：能指出“对象存在但颜色错误”“数量不对”等具体失败。
- 比单一整图文 cosine 更容易覆盖长 prompt 的多个要素。
- 问题与答案可预先固定，VQA 模块可替换，支持本地开放模型。
- 原始工作显示其与人工作文图忠实度判断的一致性优于多种传统自动指标。

## 局限

- QG 可能遗漏条件、产生重复/非原子问题，或生成 prompt 并未蕴含的问题。
- VQA 自由回答受同义词、格式和模型能力影响；字符串判对可能误杀正确答案。
- 独立问题之间没有依赖约束：图中“没有摩托车”时，继续回答“摩托车是蓝色”会造成语义不一致；DSG 正是针对此类问题改进。
- 主要评语义忠实度，不直接测美学、自然度或人类偏好。
- 更换 QG、VQA、答案规范化规则会改变结果，不能沿用原论文数值口径。

## 推荐用法

- 用官方 QA 和 mPLUG-large 复现原始 TIFA；自定义 prompt 时公开全部 QA。
- 除 overall 外，按对象、属性、数量、空间、活动、文字等题型给分项。
- 人工抽审问题本身，分别报告“问题生成错误”和“图像回答错误”，避免把 judge 错误归咎于生成模型。
- 对依赖关系和重复问题敏感时，使用 [DSG](../05_DSG/)；需要软概率和联合满足时使用 [Soft-TIFA](../07_GenEval2_SoftTIFA/)。

## 官方来源与代码

- Hu et al., **TIFA: Accurate and Interpretable Text-to-Image Faithfulness Evaluation with Question Answering**, ICCV 2023：[论文](https://arxiv.org/abs/2303.11897)
- 项目页：[tifa-benchmark.github.io](https://tifa-benchmark.github.io/)
- 官方代码、QA 与人工标注：[Yushi-Hu/tifa](https://github.com/Yushi-Hu/tifa)

```python
from tifascore import tifa_score_benchmark
results = tifa_score_benchmark(
    "mplug-large",
    "tifa_v1.0/tifa_v1.0_question_answers.json",
    "your_images.json"
)
```
