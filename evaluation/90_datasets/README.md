# 数据集索引（33 个数据集/数据套件）

> 每张卡记录规模、标注、适用指标和版本坑。规模优先采用原论文/官方 README；不同 split、过滤集和维护版分开说明。使用前请再次检查最新数据卡、许可和下载完整性。

## A. 通用 prompt、组合与知识

| 数据集 | 核心规模 | 主要用途 |
|---|---|---|
| [MS COCO](01_MSCOCO/) | val2014 40,504 图；常见抽样30k prompts | FID/CMMD 真实参考与通用 caption |
| [DrawBench](02_DrawBench/) | 200 prompts | 多挑战通用生成与人工评价 |
| [PartiPrompts](03_PartiPrompts/) | 1,600 prompts | 类别/challenge 分层评价 |
| [TIFA v1.0](04_TIFA-v1/) | 约4,000文本、约2.5万QA | 可解释问答式对齐 |
| [DSG-1k](05_DSG-1k/) | 1,060 prompts、8类 | 依赖图式细粒度对齐 |
| [GenEval](06_GenEval/) | 553 prompts、6类 | 检测式对象组合 |
| [GenEval 2](07_GenEval2/) | 800 prompts、原子QA | Soft-TIFA、原子数/技能分析 |
| [GenAI-Bench](08_GenAI-Bench/) | 1,600 prompts、38.4k人工评分 | 组合生成与评分器验证 |
| [T2I-CompBench++](09_T2I-CompBenchPP/) | 8,000 prompts、8子类 | 属性/关系/数量/复杂组合 |
| [DPG-Bench](10_DPG-Bench/) | 1,065稠密prompts | 长文本实体/属性/关系覆盖 |
| [WISE](11_WISE/) | 1,000 prompts、25子域 | 世界知识与推理 |
| [OneIG-Bench](12_OneIG-Bench/) | 1,320 prompt定义、6集 | 对齐/文字/推理/风格/多语言/多样性 |
| [Gecko2K](13_Gecko2K/) | 约2k prompts、约100k人工标注 | 技能覆盖与三种元评价 |
| [HEIM](32_HEIM/) | 原版62场景、12方面、25指标 | 全面评价框架 |

## B. 人类偏好与生成图质量标注

| 数据集 | 核心规模 | 主要用途 |
|---|---|---|
| [Pick-a-Pic](14_Pick-a-Pic/) | v1约50万；v2超100万示例 | 真实用户成对偏好 |
| [HPD v2](15_HPDv2/) | 798k选择、430k+图、107k prompts | HPS v2训练/验证与风格benchmark |
| [HPD v3](16_HPDv3/) | 1.08M图文、1.17M比较 | 跨模型代际的宽谱偏好 |
| [ImageRewardDB](17_ImageRewardDB/) | 8,878 prompts、136,892比较 | 专家偏好与ImageReward |
| [MHP](18_MHP/) | 918,315标注、607,541图 | 整体/美学/对齐/细节偏好 |
| [VisionRewardDB-Image](19_VisionRewardDB/) | 约48K×60维 | 可解释多维偏好 |
| [AGIQA-3K](20_AGIQA-3K/) | 2,982生成图 | 感知质量与对齐MOS |
| [EvalMuse-40K](21_EvalMuse-40K/) | 4k prompts、40k样本、1M+标注 | 元素级对齐与结构问题 |

## C. 编辑、个性化与多模态条件

| 数据集 | 核心规模 | 主要用途 |
|---|---|---|
| [PIE-Bench](22_PIE-Bench/) | 700图、10类、人工mask | 编辑成功/结构/背景保持 |
| [GEdit-Bench](23_GEdit-Bench/) | 606实例、11类、中英文 | 真实指令、SC/PQ/O |
| [MagicBrush](24_MagicBrush/) | 5,313 sessions、10,388 turns | 单/多轮、有/无mask编辑 |
| [ImgEdit-Bench](25_ImgEdit-Bench/) | 734基础+47困难+多轮 | 指令/质量/保持/记忆回滚 |
| [DreamBench](26_DreamBench/) | 30 subjects、25 prompts | DINO-I/CLIP-I/CLIP-T |
| [DreamBench++](27_DreamBenchPP/) | 150参考图、1,350 prompts | CP/PF人工对齐评价 |
| [MMIG-Bench](28_MMIG-Bench/) | 4,850 prompts、1,750参考图、380主体 | 多模态输入、AMS与身份保持 |

## D. 视觉文字与参考分布

| 数据集 | 核心规模 | 主要用途 |
|---|---|---|
| [AnyText-Benchmark](29_AnyText-Benchmark/) | 英文1,000+中文1,000 | 多语言文字生成/编辑 |
| [CVTG-2K](30_CVTG-2K/) | 2,000 prompts、2–5文字区 | 多区域复杂视觉文字 |
| [TextAtlasEval](31_TextAtlasEval/) | 约3,000评测样本 | 长/稠密文字与CER |
| [MJHQ-30K](33_MJHQ-30K/) | 30k图、10类×3k | 高审美MJ参考分布与FID |

## 选择建议

- **组合语义**：GenEval 2 + DPG-Bench；需要检测式可解释结果再加 GenEval/T2I-CompBench。
- **验证自动评分器**：GenAI-Bench、Gecko2K、EvalMuse-40K、AGIQA-3K，按任务选择人工标签。
- **训练偏好模型**：Pick-a-Pic/HPD/ImageReward/MHP/VisionRewardDB，但必须保留独立外部人工集。
- **编辑**：PIE 有 mask，GEdit 真实中英文指令，MagicBrush 有人工目标与多轮，ImgEdit 补困难定位/回滚。
- **个性化**：DreamBench 便于历史比较，DreamBench++/MMIG 更适合新模型细粒度评价。
- **文字**：AnyText 测中英短文本，CVTG 测多区域，TextAtlasEval 测长/稠密文本。
- **分布**：COCO 是自然照片参考，MJHQ 是筛选后的生成图参考，两者语义不同，不可把 FID 直接横比。

## 通用数据卡核对项

- 数据版本、commit、下载日期与文件校验；
- train/dev/test 是否按 prompt、主体或 session 去重；
- 图像、文本、标注分别的许可与隐私要求；
- 是否含商业模型输出、是否允许再分发/商用；
- 是否已被待评模型或评审器训练使用；
- 公开 prompt 是否需要保留原语言、标点、改写和负向指令。
