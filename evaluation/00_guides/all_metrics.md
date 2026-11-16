# 53 张指标/评分方法卡总索引

## 01 文图对齐与组合性（12）

| 指标 | 输入/性质 | 分数方向与核心用途 |
|---|---|---|
| [CLIPScore](../01_alignment/01_CLIPScore/) | 单图+文本，参考自由 | ↑ 整体语义 cosine 基线 |
| [BLIPScore / ITC / ITM](../01_alignment/02_BLIPScore/) | 单图+文本 | ↑ BLIP 相似度或匹配概率，需写明具体头 |
| [VQAScore](../01_alignment/03_VQAScore/) | 单图+文本、生成式VQA | ↑ 回答 Yes 的连续概率 |
| [TIFA](../01_alignment/04_TIFA/) | prompt QA+生成图 | ↑ 问题正确率，可解释 |
| [DSG](../01_alignment/05_DSG/) | 原子问题+依赖图+生成图 | ↑ 依赖归零后的问题正确率 |
| [GenEval](../01_alignment/06_GenEval/) | 553 prompts+检测器 | ↑ 六类对象组合宏平均 |
| [GenEval 2 / Soft-TIFA](../01_alignment/07_GenEval2_SoftTIFA/) | 800 prompts+原子概率 | ↑ AM测原子、GM测整prompt |
| [T2I-CompBench++](../01_alignment/08_T2I-CompBench/) | 8k prompts、多评分器 | ↑ 八类组合能力分项 |
| [DPG-Bench](../01_alignment/09_DPG-Bench/) | 1,065长prompts+mPLUG | ↑ 稠密语义覆盖 |
| [WISE / WiScore](../01_alignment/10_WISE_WiScore/) | 1,000知识prompts+VLM | ↑ 原版三维加权或Verified二值分 |
| [OneIG-Bench](../01_alignment/11_OneIG-Bench/) | 六prompt集、多评分器 | ↑ 对齐/文字/推理/风格/多样性分项 |
| [VIEScore](../01_alignment/12_VIEScore/) | 条件+输出+MLLM | ↑ SC/PQ及√(SC×PQ)，带理由 |

## 02 人类偏好与奖励模型（6）

| 指标 | 骨干/数据 | 分数方向与核心用途 |
|---|---|---|
| [PickScore](../02_preference/01_PickScore/) | CLIP-H、Pick-a-Pic v1 | ↑ 同prompt真实用户偏好 |
| [HPS v2 / v2.1](../02_preference/02_HPSv2/) | CLIP系、HPD v2 | ↑ 人类偏好及四风格benchmark |
| [HPS v3](../02_preference/03_HPSv3/) | Qwen2-VL、HPD v3 | ↑ 宽谱偏好均值与不确定性 |
| [ImageReward](../02_preference/04_ImageReward/) | BLIP、137k专家比较 | ↑ 通用文生图偏好奖励 |
| [MPS](../02_preference/05_MPS/) | 条件化CLIP、MHP | ↑ 整体/美学/对齐/细节；公开权重限制需注意 |
| [VisionReward](../02_preference/06_VisionReward/) | CogVLM2、细粒度QA | ↑ 多问题可解释加权偏好 |

## 03 美学与感知画质（4）

| 指标 | 输入 | 分数方向与核心用途 |
|---|---|---|
| [Aesthetic Predictor](../03_quality/01_AestheticPredictor/) | 单图、CLIP特征+回归头 | ↑ 美学，不测对齐；checkpoint决定尺度 |
| [CLIP-IQA](../03_quality/02_CLIP-IQA/) | 单图+正反提示 | ↑ 正向质量/观感属性概率 |
| [MUSIQ](../03_quality/03_MUSIQ/) | 原生分辨率单图 | ↑ 多尺度无参考质量，checkpoint决定尺度 |
| [Q-Align / OneAlign](../03_quality/04_Q-Align/) | 单图+评分问题 | ↑ 五等级概率加权质量/美学分 |

## 04 分布、保真与多样性（8）

| 指标 | 输入 | 分数方向与核心用途 |
|---|---|---|
| [Inception Score](../04_distribution/01_IS/) | 生成图集合 | ↑ 类别可辨识+类别多样；旧基线 |
| [FID](../04_distribution/02_FID/) | 生成+参考集合 | ↓ Inception高斯特征分布距离 |
| [KID](../04_distribution/03_KID/) | 生成+参考集合 | ↓ Inception多项式核无偏MMD |
| [CMMD](../04_distribution/04_CMMD/) | 生成+参考集合 | ↓ CLIP+RBF核MMD |
| [FD-DINOv2](../04_distribution/05_FD-DINOv2/) | 生成+参考集合 | ↓ DINOv2特征Fréchet距离 |
| [Precision / Recall](../04_distribution/06_Precision-Recall/) | 两个集合 | ↑ 分别测真实流形保真与覆盖 |
| [Density / Coverage](../04_distribution/07_Density-Coverage/) | 两个集合 | ↑ 高密度保真与真实覆盖；Density可>1 |
| [Vendi Score](../04_distribution/08_VendiScore/) | 样本集合+相似度核 | ↑ 有效不同元素数，适合同prompt多样性 |

## 05 配对图像与参考一致性（7）

| 指标 | 输入 | 分数方向与核心用途 |
|---|---|---|
| [PSNR](../05_pairwise_reference/01_PSNR/) | 对齐输出+目标图 | ↑ 像素MSE的dB形式 |
| [SSIM / MS-SSIM](../05_pairwise_reference/02_SSIM/) | 对齐输出+目标图 | ↑ 亮度/对比/结构相似 |
| [LPIPS](../05_pairwise_reference/03_LPIPS/) | 配对图或组内图对 | ↓ 深度感知距离；组内作多样性时反向解读 |
| [CLIP-I](../05_pairwise_reference/04_CLIP-I/) | 参考图+生成图 | ↑ 图像语义/主体保持 |
| [DINO-I](../05_pairwise_reference/05_DINO-I/) | 参考图+生成图 | ↑ 自监督视觉主体保持 |
| [Directional CLIP](../05_pairwise_reference/06_DirectionalCLIP/) | 源/目标图+源/目标文本 | ↑ 编辑变化方向一致 |
| [Masked Preservation](../05_pairwise_reference/07_MaskedPreservation/) | 源/编辑图+mask | 背景PSNR/SSIM↑，MSE/LPIPS↓ |

## 06 编辑与多模态条件生成（7）

| 指标/套件 | 数据/方法 | 核心用途 |
|---|---|---|
| [PIE-Bench](../06_editing_multimodal/01_PIE-Bench/) | 700图+人工mask | 结构、背景、文本、效率四维编辑 |
| [GEdit-Bench](../06_editing_multimodal/02_GEdit-Bench/) | 606真实实例+MLLM | 11类SC/PQ/O，中英文 |
| [I²EBench](../06_editing_multimodal/03_I2EBench/) | 2k+图、4k+指令 | 16维编辑与改写稳健性 |
| [DreamBench++](../06_editing_multimodal/04_DreamBenchPP/) | 150参考图、1,350 prompts | CP/PF双轴0–4评分 |
| [RefVNLI](../06_editing_multimodal/05_RefVNLI/) | 参考图+prompt+目标图 | 一次输出文本对齐与主体保持 |
| [MMIG-Bench / AMS](../06_editing_multimodal/06_MMIG-Bench/) | 多模态条件+三层指标 | 身份/伪影/细粒度语义/偏好 |
| [Control Consistency](../06_editing_multimodal/07_ControlConsistency/) | 条件+输出+独立预测器 | mIoU/mAP/OKS/边缘F1/深度误差 |

## 07 视觉文字渲染（4）

| 指标 | 分数方向 | 核心用途 |
|---|---|---|
| [OCR / Sentence Accuracy](../07_text_rendering/01_OCR-Accuracy/) | ↑ | 整行/整区域/整图完全正确率 |
| [NED](../07_text_rendering/02_NED/) | 本卡相似度定义↑ | 归一化编辑距离的部分正确信用 |
| [CER / WER](../07_text_rendering/03_CER-WER/) | ↓ | 字符/词的替换删除插入错误率 |
| [OCR-F1](../07_text_rendering/04_OCR-F1/) | ↑ | 同时惩罚多字、漏字、错字与区域错误 |

## 08 人工评价与统计（5）

| 方法 | 核心用途 |
|---|---|
| [MOS / DMOS](../08_human_statistics/01_MOS/) | 多标注者绝对意见分与差分分 |
| [Pairwise Win Rate](../08_human_statistics/02_PairwiseWinRate/) | 同条件A/B/tie胜率与区间 |
| [Elo / Bradley–Terry](../08_human_statistics/03_Elo-BradleyTerry/) | 多模型两两偏好拟合为相对rating |
| [Agreement](../08_human_statistics/04_Agreement/) | κ/α/Kendall W/ICC等标注一致性 |
| [SRCC / PLCC / KRCC](../08_human_statistics/05_Correlation/) | 自动指标与人工分的元评价相关性 |

下一步：[33 个数据集索引](../90_datasets/) · [任务选择矩阵](selection_matrix.md) · [复现协议](protocol.md)
