# WISE 与 WiScore（原版 / WISE_Verified）

## 一句话介绍

WISE 评估模型能否把 prompt 中隐含的**世界知识、文化常识、时空推理和自然科学知识**转成正确图像，而非只做显式名词到像素的匹配。

- **数据**：1,000 条 prompt，25 个子领域
- **三大类**：Cultural Common Sense、Spatio-temporal Reasoning、Natural Science
- **六大汇总类**：Culture、Time、Space、Biology、Physics、Chemistry
- **重要版本变化**：原版 WiScore 是三维 0–2 加权分；2026 年默认 WISE_Verified 改为开放 VLM judge 的二值 0/1 分，二者不可直接比较

## 原版 WiScore

原版使用 **GPT-4o-2024-05-13** 独立评价三个维度，各为 0、1、2：

- Consistency：知识答案与关系是否符合 prompt；
- Realism：是否可信、真实；
- Aesthetic Quality：构图与视觉吸引力。

单图：

`WiScore = (0.7*Consistency + 0.2*Realism + 0.1*Aesthetic)/2`

除以 2 后归一到约 0–1。总分为六类加权：

`Overall = 0.4*Culture + 0.167*Time + 0.133*Space + 0.1*Biology + 0.1*Physics + 0.1*Chemistry`

原版还分析将知识型 prompt 改写为显式答案前后的分数差：例如将“母亲节常赠的植物”改成“康乃馨”。差值可帮助区分“不知道画什么”与“知道答案但画不好”，但它依赖改写质量和同一评分协议，不能单独当知识准确率。

## WISE_Verified（2026 默认）

官方维护版仍保留 1,000 条 ID 和知识评测目标，但：

- 刷新约 200 条 prompt；
- 默认 judge 改为通过 vLLM 服务的 **Qwen3.5-35B-A3B**；
- 每图 WiScore 改为 0/1：知识含义正确、关键关系正确，并且现实性/视觉可用性足以验证才为 1；
- 不再分别输出 realism 和 aesthetic；
- 六大类总体权重改为：`0.40*Culture + 0.12*(Time+Space+Biology+Physics+Chemistry)`。

官方明确说明 **WISE_Verified 不是 WISE 2.0**，而是便于开放、低成本复现的维护更新。

## 优点

- 专门区分“文本对齐”与“隐含知识落地”，补足 GenEval 等对象组合基准的盲区。
- 每条 prompt 带解释，可让 judge 知道期望的知识答案，而非凭自身猜测。
- 覆盖文化、时间、空间、生物、物理、化学，能分域诊断。
- 新旧版本均给出明确类别聚合权重。

## 局限

- judge 必须既看懂图又知道正确答案；judge 的知识错误会误判生成模型。
- 原版权重把审美和真实感混入知识分，因此 WiScore 不是纯知识准确率；Verified 二值分也会受“太模糊/不现实而无法判断”的影响。
- 一些知识 prompt 存在多个合理视觉答案，解释和标注需要持续维护。
- 闭源 GPT-4o 旧快照复现受限；Verified 与原版的 prompt、judge、分数和权重均变，不能拼成时间序列。
- 艺术风格任务中 realism 的定义应谨慎，不能天然奖励照片感而惩罚合理的非写实风格。

## 推荐报告

必须写 `WISE-original/GPT-4o-2024-05-13` 或 `WISE_Verified/Qwen3.5-35B-A3B`，并给六类分项、prompt 版本和原始 judge 回复。若要单独研究知识，建议另报 consistency/知识正确项，避免 overall 被画质权重混淆。

## 官方来源

- Niu et al., **WISE: World Knowledge-Informed Semantic Evaluation for Text-to-Image Generation**：[论文](https://arxiv.org/abs/2503.07265)
- 官方代码、原版归档与 Verified：[PKU-YuanGroup/WISE](https://github.com/PKU-YuanGroup/WISE)
