# VQAScore

## 一句话介绍

把“这张图是否符合这段文本？”变成一个视觉问答问题，用生成式 VQA 模型回答 **Yes** 的概率作为连续对齐分；比只读完整文本答案的 VQA 方法更能保留不确定性。

- **输入**：生成图与原始文本
- **输出**：通常 `[0,1]`，越高越对齐
- **原始推荐 judge**：CLIP-FlanT5，论文结果常用 `clip-flant5-xxl`
- **配套基准**：GenAI-Bench / GenAI-Rank

## 原始定义

对文本 `t`，构造类似：

> Does this figure show "{t}"? Please answer yes or no.

则：

`VQAScore(x,t) = P_VQA("Yes" | x, question(t))`

对数据集通常先逐图计算，再取均值。分数是模型输出概率，不是经人类校准的真实正确概率。

当前开源实现还允许自定义 question/answer 模板；当 answer 是多 token 时，可采用实现规定的 token 概率聚合。此类扩展与原始单 Yes 分数应标为不同协议。

## 与 TIFA/DSG 的差别

- VQAScore 可以直接用**整段 prompt**问一个问题，无需 LLM 先拆 QA，因此简单、避免问题生成错误。
- TIFA/DSG 将 prompt 拆成多个可解释问题，能定位漏掉的对象/属性；计算更多次。
- Soft-TIFA 将多个原子问题的**正确答案概率**做算术或几何聚合，兼顾软分数与组合性。

## 配套数据集

**GenAI-Bench** 含 1,600 条专业设计师来源的挑战性 prompt，带 5,000+ 人工核验技能标签；论文发布 38,400 个 1–5 级人工对齐评分，用于检验自动指标。可分别分析基础组合与含高级组合的 prompt。

**GenAI-Rank** 用于成对/排序一致性验证。验证自动评分器时，应区分实例级成对准确率、点评分相关性与模型级排序相关性。

## 优点

- 单个 VQA 问题即可得到软分数，避免自由回答严格字符串匹配的损失。
- 原始论文及后续采用表明，它在复杂组合对齐上通常明显优于朴素 CLIPScore。
- 保留逐样本分，易与人工 1–5 分或成对偏好比较。
- 可扩展至视频/3D 等 text-to-visual 任务，但不同模态协议需分别验证。

## 局限与复现风险

- judge 自己可能漏看、幻觉或受语言先验影响；Yes 概率高不等于图中所有原子条件都正确。
- 整段长 prompt 只问一次，难以知道具体失败位置；可配合原子问题或场景图方法。
- 不同 VLM 的 Yes/No 校准差异很大，**不可把 CLIP-FlanT5 的分与 Qwen/GPT/Gemini 的分直接比较**。
- 依赖 logprobs 的商业模型接口可能变化；若模型不暴露所需 token 概率，不能悄悄改用自报分数还叫同一 VQAScore。
- 大模型 judge 成本高；GPU 显存、推理时长和 API 版本应纳入报告。

## 版本提醒（重要）

官方 `t2v_metrics` 已将后续模型支持推进到新版本。复现 2024 年 VQAScore/GenAI-Bench 论文，官方 README 建议使用 **legacy v3.0 / `t2v-metrics==3.0`**；后续版本支持更新的开放与商业 VLM，但属于不同 judge 配置。

## 官方来源与最小调用

- Lin et al., **Evaluating Text-to-Visual Generation with Image-to-Text Generation (VQAScore)**, ECCV 2024：[论文](https://arxiv.org/abs/2404.01291)
- Li et al., **GenAI-Bench**, CVPR 2024 workshop：[论文](https://arxiv.org/abs/2406.13743)
- 官方代码：[linzhiqiu/t2v_metrics](https://github.com/linzhiqiu/t2v_metrics)

```python
import t2v_metrics
scorer = t2v_metrics.VQAScore(model="clip-flant5-xxl")  # 原论文复现用legacy环境
score = scorer(images=["sample.png"], texts=["a red cube left of a blue sphere"])
```

> 报告时至少写：`VQAScore / CLIP-FlanT5-XXL / t2v-metrics version / question template / 每prompt图数 / 聚合方式`。
