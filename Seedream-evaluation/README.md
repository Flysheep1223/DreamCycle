# Seedream 类通用生图模型：推荐评估维度与示例

> 这是一套面向 **Seedream 及同类高能力通用生图模型**的实操指南。重点不是堆指标，而是回答：模型是否听懂、是否画对、文字是否可用、是否保持参考内容，以及人是否更愿意使用。
>
> **所有带分数的案例都是虚构演示，仅用于说明计算方法，不代表 Seedream 或任何其他模型的实测结果。**
>
> 本目录采用单层结构：每个方法/维度对应一个 Markdown 文档，不再设置子文件夹。

## 一、先选哪几个？

### 最小评测包：文生图必做

1. [组合指令遵循：GenEval 2 / Soft-TIFA](01_GenEval2_SoftTIFA.md)
2. **私有 prompt 集上的 [VQAScore](02_VQAScore.md)**；长 prompt 加 [DPG-Bench](03_DPG-Bench.md)
3. [文字渲染：OCR Accuracy、NED、CER、OCR-F1](04_OCR_TextRendering.md)
4. [人工成对盲测胜率 + HPS v3 辅助](05_HumanPreference_HPSv3.md)
5. [感知画质：Q-Align + 人工质量检查](06_QAlign_PerceptualQuality.md)

### 按模型能力增加

- 宣称知识/推理能力：[WISE / WiScore](07_WISE_WiScore.md)
- 需要分析多 seed 多样性：[Vendi Score](08_VendiScore.md)
- 支持指令编辑：[GEdit-Bench](09_GEdit-Bench.md) + [背景保持](10_MaskedBackgroundPreservation.md)
- 支持参考图、主体保持、多图输入：[DINO-I、CLIP-I、DreamBench++、MMIG](11_SubjectReference.md)

## 二、文档索引与各自回答的问题

| 文档 | 指标维度 | 核心问题 | 推荐级别 |
|---|---|---|---|
| [00_protocol.md](00_protocol.md) | 实验协议 | 怎样保证各模型比的是同一件事？ | 必读 |
| [01_GenEval2_SoftTIFA.md](01_GenEval2_SoftTIFA.md) | Soft-TIFA AM/GM | 每个条件画了多少？整条 prompt 是否全部满足？ | 文生图核心 |
| [02_VQAScore.md](02_VQAScore.md) | VQAScore | 生成图整体上是否符合文本？ | 文生图核心 |
| [03_DPG-Bench.md](03_DPG-Bench.md) | DPG-Bench | 长而稠密的要求有没有漏项？ | 强烈建议 |
| [04_OCR_TextRendering.md](04_OCR_TextRendering.md) | OCR 系列 | 文字是否完全正确、错多少、是否多漏字？ | 强烈建议 |
| [05_HumanPreference_HPSv3.md](05_HumanPreference_HPSv3.md) | 胜率、HPS v3 | 人更愿意选哪个模型？ | 最终排名核心 |
| [06_QAlign_PerceptualQuality.md](06_QAlign_PerceptualQuality.md) | Q-Align、人工 PQ | 是否自然、清晰、少伪影？ | 必要辅助 |
| [07_WISE_WiScore.md](07_WISE_WiScore.md) | WiScore | 隐含世界知识是否画对？ | 能力宣称时必做 |
| [08_VendiScore.md](08_VendiScore.md) | Vendi Score | 同 prompt 多次生成是否有意义的变化？ | 可选 |
| [09_GEdit-Bench.md](09_GEdit-Bench.md) | GEdit SC/PQ/O | 编辑是否按指令完成且自然？ | 编辑核心 |
| [10_MaskedBackgroundPreservation.md](10_MaskedBackgroundPreservation.md) | mask 外 LPIPS/PSNR/SSIM | 不该改的地方有没有被改坏？ | 编辑核心 |
| [11_SubjectReference.md](11_SubjectReference.md) | DINO-I、CLIP-I、CP/PF、AMS | 还是不是同一个主体？新 prompt 是否完成？ | 参考图核心 |
| [12_JudgeTypes_and_Prompts.md](12_JudgeTypes_and_Prompts.md) | 评审器类型与提示词 | 哪些用通用 VLM、哪些用微调评分模型、各自怎么提问？ | 复现必读 |
| [13_Seedream_Capability_Metrics.md](13_Seedream_Capability_Metrics.md) | **三类能力分榜方案** | 文生图、指令编辑、参考图与多模态，三类分别用哪些指标？ | **全能力评测入口** |
| [14_Realtime_Machine_Evaluation.md](14_Realtime_Machine_Evaluation.md) | **实时机评架构** | 生成后如何自动判断任务类型、并行调用 VLM/OCR/专项指标？ | **在线落地入口** |
| [15_Router_Workflow.md](15_Router_Workflow.md) | **路由器内部工作流** | 如何规则初筛、多标签识别、冲突校验并生成评分计划？ | 路由实现 |
| [16_Score_Normalization.md](16_Score_Normalization.md) | **多路分数归一与聚合** | 编辑、参考图、OCR 等多路结果如何形成可解释的在线分？ | 分数汇总 |

## 三、人评与 AI 评对照

| 文档/方法 | 主要评价方式 | 人评部分 | AI/自动评分部分 |
|---|---|---|---|
| [GenEval 2 / Soft-TIFA](01_GenEval2_SoftTIFA.md) | **AI 评** | 无；数据和问题预先准备 | VQA 模型回答各原子问题，计算 AM/GM |
| [VQAScore](02_VQAScore.md) | **AI 评** | 无 | VLM 输出回答 Yes 的概率 |
| [DPG-Bench](03_DPG-Bench.md) | **AI 评** | 无 | mPLUG-large 回答依赖图问题并自动聚合 |
| [OCR 文字渲染](04_OCR_TextRendering.md) | **AI/自动评** | 可选人工抽检，不是默认评分步骤 | OCR 识别后自动计算 Accuracy、NED、CER/WER、F1 |
| [成对胜率 + HPS v3](05_HumanPreference_HPSv3.md) | **人评 + AI 评** | **匿名 A/B/tie 投票、人工整体偏好** | HPS v3 输出偏好均值；多模型可用算法拟合 Elo/BT |
| [Q-Align + 人工 PQ](06_QAlign_PerceptualQuality.md) | **人评 + AI 评** | **人工按 1–5 评价画质、勾选伪影类型** | Q-Align/OneAlign 输出五等级概率并加权 |
| [WISE / WiScore](07_WISE_WiScore.md) | **AI 评** | 题目和标准知识解释可经人工整理，但正式打分不是人评 | 原版 GPT-4o 或 Verified Qwen judge 评分 |
| [Vendi Score](08_VendiScore.md) | **AI/自动评** | 无 | 相似度模型构建矩阵，自动计算有效不同元素数 |
| [GEdit-Bench](09_GEdit-Bench.md) | **AI 评** | 无 | GPT 或 Qwen judge 输出 SC、PQ，再计算 Overall |
| [背景保持](10_MaskedBackgroundPreservation.md) | **自动计算，部分使用 AI** | 编辑 mask 可来自人工标注，但评分不是人评 | PSNR/SSIM 是传统算法；LPIPS 使用学习的深度特征 |
| [主体与参考图保持](11_SubjectReference.md) | **以 AI 评为主，可辅以人评** | 可选人工判断“是否同一主体”和文本遵循 | DINO-I、CLIP-I、VQAScore、GPT-4o CP/PF、Qwen AMS |

### 容易混淆的三点

1. **HPS v3 不是人评**：它使用人类偏好数据训练，但正式评分时由 AI 模型推理。
2. **DreamBench++ 的“Human-Aligned”不是人评**：表示目标是贴近人工判断，默认 CP/PF 分数由 GPT-4o 给出。
3. **人工标注数据不等于本次人评**：例如人工编辑 mask、人工整理 QA，只是评分输入；真正的本次人评需要评审者对输出图进行打分、排序或投票。

推荐实践是：**AI 指标用于全量、逐样本、可重复评分；人工成对盲测用于代表性子集和最终模型排序校验。**

进一步查看：**[哪些方法使用通用 VLM、哪些使用微调评分模型，以及提示词示例](12_JudgeTypes_and_Prompts.md)**。

## 四、推荐报告形式

不要把所有原始分相加。建议保留下面这张分维度结果表：

| 维度 | 主结果 | 必须同时报告 |
|---|---|---|
| 组合对齐 | Soft-TIFA GM ↑ | AM、按技能分项、有效 prompt 数 |
| 通用语义 | VQAScore ↑ | judge 版本、语言分项、95% CI |
| 长 prompt | DPG Overall ↑ | Entity/Attribute/Relation 等分项 |
| 文字 | Sentence Accuracy ↑ | NED、CER、OCR-F1、OCR 版本 |
| 人类偏好 | 成对胜率 ↑ | 平局率、票数、95% CI、评审维度 |
| 感知质量 | Q-Align/人工 PQ ↑ | 典型伪影比例、低分样本 |
| 编辑 | GEdit O ↑ | SC、PQ、背景保持 |
| 主体保持 | CP/PF 或 DINO-I/VQAScore | 主体遗漏/串换、参考图裁剪协议 |

## 五、为什么不把 FID、CLIPScore 放在主榜？

- **CLIPScore** 可以作历史 baseline，但对“颜色绑错、数量差一、左右反转、文字错一个字符”不够敏感。
- **FID/CMMD** 比较两组图像的分布，不读取 prompt。参考域若是 COCO，低距离可能只表示更像 COCO 自然照片。
- **Aesthetic Score** 只看美观，无法判断有没有画出用户要求。
- **HPS/PickScore/ImageReward** 是学习到的偏好分，适合辅助筛选，但会受训练数据代际和奖励过优化影响，最终结论应由人工盲测校准。

## 六、建议执行顺序

1. 先阅读 [评测协议](00_protocol.md)，冻结 prompt、seed、模型版本、输出配置和 judge。
2. 跑自动指标，保存每张图和逐题/逐样本原始分。
3. 做分项分析，找出数量、空间、文字、长 prompt、人物等弱项。
4. 在相同私有 prompt 上做匿名 A/B 人工比较，验证自动指标能否复现模型排序。
5. 公开总体、分项、置信区间和失败案例，不只展示精选好图。

原始指标的完整论文与实现见各文档末尾，以及主资料库的 [工具与来源索引](../evaluation/99_appendix/resources.md)。
