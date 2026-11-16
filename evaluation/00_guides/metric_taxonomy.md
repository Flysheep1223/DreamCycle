# 指标分类：先明确“测什么”与“对什么取平均”

## 1. 六个正交评价轴

| 轴 | 典型失败 | 合适指标 | 不能由它推出的结论 |
|---|---|---|---|
| 文图对齐 | 漏对象、错颜色、错数量、错关系 | VQAScore、TIFA、DSG、GenEval、Soft-TIFA | 不保证美观、自然或人类更喜欢 |
| 感知质量/美学 | 模糊、伪影、手部异常、构图差 | Q-Align、CLIP-IQA、MUSIQ、Aesthetic Predictor、人工 PQ | 不保证 prompt 被遵循 |
| 人类偏好 | 综合体验差 | PickScore、HPS、ImageReward、MPS、VisionReward、成对盲测 | 不是可解释的单项错误率；有人群和数据域偏置 |
| 参考一致性 | 编辑过度、身份/主体改变 | DINO-I、CLIP-I、RefVNLI、掩码外指标 | 高相似度可能只是“没有编辑” |
| 分布质量与覆盖 | 模式坍缩、整体不自然、覆盖不足 | FID、KID、CMMD、Precision/Recall、Density/Coverage | 不证明单条 prompt 对齐，也不等同于偏好 |
| 专项能力 | 拼写错误、姿态错误、条件不遵守 | OCR 系列、OKS、mIoU、mAP、深度误差 | 不能替代整体质量和人工体验 |

## 2. 按输入形式分类

### 单样本、参考自由（reference-free）

输入一张生成图及可选 prompt，输出分数：CLIPScore、VQAScore、PickScore、HPS、ImageReward、Q-Align、CLIP-IQA。它们适合做大规模 prompt 评测和同 prompt 候选排序。

### 单样本、带参考（reference-based）

输入输出图与源图/目标图/参考主体：PSNR、SSIM、LPIPS、CLIP-I、DINO-I、RefVNLI。必须说明参考图扮演的是“唯一标准答案”还是“仅需保持某些属性”。

### 集合级、双分布

输入生成集和真实/参考集：FID、KID、CMMD、Precision/Recall、Density/Coverage。样本数、特征提取器、resize、参考 split 都会改变结果。

### 集合级、参考自由

Inception Score、Vendi Score、组内 LPIPS 多样性。IS 需要分类器；Vendi 需要相似度核。它们可在没有真实参考集时估计集合性质，但也更容易被单一维度“刷分”。

### 基准流水线（benchmark + scorer）

GenEval、TIFA、DSG、T2I-CompBench、DPG-Bench、GEdit-Bench 等既包含 prompt/图像数据，也规定问题生成、检测/VQA judge 和聚合方式。换数据或换 judge 后，应视为新协议。

## 3. 聚合层级比公式本身更容易被忽略

- **图像级**：一张图一个分，最后对图像取均值。简便，但长 prompt 与短 prompt 权重相同。
- **问题/原子级**：一张图多个问题。若直接平均所有问题，多问题 prompt 权重更大；若先平均到 prompt，则每条 prompt 权重相同。
- **prompt 全对率**：所有必要条件都满足才算成功，严格但对单个小错误非常敏感。
- **几何均值**：任何必要条件接近 0 都会显著拉低总分，适合表达“联合满足”；Soft-TIFA GM 即用于 prompt-level 估计。
- **任务宏平均**：先在每类任务内平均，再对任务取均值，避免大类任务支配总分。必须说明是否另报微平均。
- **多 seed 平均**：`E_seed[score]` 反映期望能力；`P(at least one of K correct)` 反映 best-of-K 能力，二者不可混用。

## 4. 指标验证指标：怎么知道一把尺是否可靠？

1. **实例级点估计相关性**：SRCC/PLCC/KRCC，回答分数是否随人工分数变化。
2. **实例级成对一致性**：对人工认为 A 优于 B 的样本，看自动指标是否同向；同时报 ties 处理规则。
3. **模型级排序相关性**：对模型平均分排序；样本量通常很小，不能替代实例级验证。
4. **对抗灵敏度**：故意删对象、交换属性、改数量、破坏文字、降低画质，检查指标是否朝预期方向变化。
5. **不变量测试**：对不影响目标属性的 resize/JPEG/裁剪做最小扰动，检查是否异常波动。
6. **新模型漂移测试**：不能只在与指标训练数据同年代的旧模型上验证。GenEval 2 的工作正说明 benchmark 会随生成模型演进而与人类判断漂移。

## 5. 最重要的边界

- 相关性高不代表因果上“提升该指标就提升真实体验”。
- 奖励模型可用于训练，不等于它是独立、不可被优化的评测器。
- 多指标一致也不能完全替代人工；它们可能共享同一 CLIP/VLM 盲区和训练数据偏置。
- 跨论文复用数字前，至少核对：prompt 版本、judge/checkpoint、分辨率、每 prompt 图数、seed、后处理、聚合方式、样本数。
