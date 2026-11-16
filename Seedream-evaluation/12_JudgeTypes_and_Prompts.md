# 评审器类型、是否使用 VLM，以及提示词示例

> 本文对专项目录中的方法按**实际评分器**分类。这里的“提示词”指交给 AI 评审器的指令，不是生图模型使用的生成 prompt。
>
> 提示词示例分为：**官方固定问法**与**理解用简化示意**。简化示意不是逐字官方模板；正式复现必须使用对应仓库的完整模板和指定 checkpoint。

## 先明确：并非所有指标都要用于 Seedream

本文后面的完整表格是**评审器类型对照**，不是要求把全部方法都放进 Seedream 评测。是否需要某项，取决于你评的是 Seedream 的纯文生图，还是它的编辑/参考图能力。

### Seedream 专用取舍表

| 方法 | 只做 Seedream 时怎么选 | 适用条件与理由 |
|---|---|---|
| **Soft-TIFA** | **文生图核心，建议保留** | 检查对象、属性、数量、空间关系及整 prompt 联合满足，适合发现 Seedream 的细粒度错误 |
| **DPG-Bench** | **文生图核心，建议保留** | 检查长而复杂的 prompt 是否漏实体、错属性、错关系 |
| **OCR 系列** | **文字能力核心，建议保留** | 中文、英文、多区域文字都应单独测；不是 VLM 主观打分 |
| **自定义 VLM 对齐/画质 rubric** | **推荐作为批量机评主线** | 最适合通过系统提示词批量实现，可分别评指令遵循、感知质量和具体失败原因 |
| **VQAScore** | **可选，不强制** | 能获得 Yes logprobs 时可按原定义实现；否则建议明确写成自定义 VQA 二值评分，不冒充原始 VQAScore |
| **WISE / WiScore** | **知识推理可选** | 只在你要验证 Seedream 的文化、自然知识、时空推理时启用 |
| **Vendi Score** | **多样性可选** | 只有每 prompt 生成多个 seed、并关心同条件输出差异时才需要 |
| **Q-Align / OneAlign** | **可选辅助，不是必需** | 可以评 Seedream 画质，但需要专用评分 checkpoint；如果已经用固定 VLM rubric 评画质，不必重复建设 |
| **HPS v3** | **可选辅助，不是必需** | 可以给 Seedream 输出偏好分，但需要专用奖励模型；不应替代针对性 VLM 评分和人评 |
| **GEdit / VIEScore** | **仅编辑任务保留** | 只有输入源图并要求 Seedream 按指令修改时才使用；纯文生图不用 |
| **背景 PSNR/SSIM/LPIPS** | **仅编辑任务保留** | 需要源图和编辑区域定义；纯文生图没有这些参考，不能使用 |
| **DINO-I / CLIP-I** | **仅参考图/主体保持任务保留** | 需要参考图；纯文生图不用 |
| **DreamBench++ CP/PF** | **仅个性化/主体驱动任务保留** | 测“是不是同一主体”与“是否完成新 prompt”，不是通用文生图必选项 |
| **MMIG-AMS** | **仅多模态/多参考任务保留** | 只有文本+参考图、多主体、多视角输入时才需要 |
| **人工成对胜率** | **单一版本可不采用** | 只评一个 Seedream 版本时没有 A/B 对手；可改为人工按 1–5 分别绝对评价对齐、画质、文字和整体可用性。比较不同 Seedream 版本时再恢复成对胜率 |

### 如果你只做 Seedream 文生图，推荐最终保留这五项

1. **Soft-TIFA AM/GM**：组合语义与整 prompt 联合满足。
2. **DPG-Bench**：长 prompt 的实体、属性、关系漏项。
3. **OCR Accuracy + NED + CER，多区域加 OCR-F1**：文字渲染。
4. **一套固定系统提示词的 VLM 对齐与画质评分**：批量覆盖私有 prompt，并输出失败原因。
5. **按任务需要选择 WISE 或 Vendi**：分别补知识推理和多样性；不需要就不加。

**GEdit、背景保持、DINO-I、CLIP-I、DreamBench++、MMIG-AMS 不应出现在纯文生图主榜中。HPS v3、Q-Align 也不是必须项。**

如果需要同时评估 Seedream 的文生图、编辑、主体保持、多参考与其他能力，请使用 **[按能力划分的完整指标方案](13_Seedream_Capability_Metrics.md)**，将这些指标分别放入对应能力分榜，而不是全部删除或全部混入同一总榜。

---

## 一、先理解三种主要评分方式

### A. 通用 VLM/MLLM 按提示词评审

向通用视觉语言模型输入图像和评价指令，让它回答 Yes/No、回答固定问题，或输出 0–10 分。

代表：**VQAScore、Soft-TIFA、DPG、WISE、GEdit/VIEScore、DreamBench++、MMIG-AMS**。

它们通常不是为某一次 Seedream 评测专门微调，但结果会受以下因素影响：

- VLM 型号与精确版本；
- 评价提示词；
- 图像输入顺序和分辨率；
- temperature、top-p；
- 答案概率提取与输出解析方式。

### B. 为评分或偏好专门训练的模型

模型本身已经用人工偏好、MOS 或特定评分数据微调，正式评测时直接输出奖励、等级概率或标量，而不是临时靠一段通用 judge prompt 获得评分能力。

代表：**HPS v3、Q-Align/OneAlign**。同类还有 PickScore、HPS v2、ImageReward、MPS、VisionReward。

其中：

- **HPS v3**：Qwen2-VL + 偏好奖励头，在 HPDv3 等偏好数据上训练，输出 `μ/σ`；不需要“请打 0–10 分”的评审提示词。
- **Q-Align**：专门训练成用 excellent/good/fair/poor/bad 等语言等级评分，仍需要质量/美学问题作为输入提示。
- **PickScore/HPS v2**：CLIP 系偏好模型，输出标量；无生成式评审理由。
- **ImageReward**：BLIP 系偏好模型，输出标量；无通用 VLM judge 提示词。

### C. 专用识别模型、embedding 或传统算法

- **OCR**：专用文字检测/识别模型，不使用通用评价提示词。
- **DINO-I/CLIP-I**：图像 embedding 余弦，不让 VLM 写评价。
- **LPIPS**：感知相似度网络，不是 VLM judge。
- **Vendi Score**：embedding + 相似度矩阵 + 数学公式。
- **PSNR/SSIM**：传统图像算法，没有 AI 模型和提示词。

---

## 二、逐个方法分类表

| 方法 | 人评/机评 | 默认评分器类型 | 是生成式 VLM 评审吗？ | 为当前评分任务专门微调吗？ | 有评价提示词吗？ |
|---|---|---|---|---|---|
| **GenEval 2 / Soft-TIFA** | **机评** | 通用 VQA/VLM；论文实验采用 Qwen3-VL-8B 等配置 | **是，回答固定原子问题** | 通常不为 Soft-TIFA 专门微调 | **有，数据中的固定 `vqa_list`**；不是自由 0–10 打分提示 |
| **VQAScore** | **机评** | 通用生成式 VQA；原始为 CLIP-FlanT5-XXL，后续可换 Qwen 等 | **是** | 不为待评生成模型专门微调 | **有固定问题模板**，取 Yes 概率 |
| **DPG-Bench** | **机评** | mPLUG-large VQA | **是，回答固定图问题** | 不为 DPG 待评模型专门微调 | **有，预生成的依赖图 QA** |
| **OCR Accuracy/NED/CER/F1** | **机评** | PaddleOCR 等专用文字检测识别模型 | **否** | **是，为 OCR 任务训练**；不是为生图评分微调 | **无**；后续字符串计算不使用提示词 |
| **HPS v3** | **机评** | 微调偏好奖励模型，Qwen2-VL 骨干 | **否，不是让模型写评分理由** | **是，使用 HPDv3 等人类偏好数据** | 输入包含生图 prompt，但**没有通用 judge 打分提示词** |
| **Q-Align / OneAlign** | **机评** | 微调视觉评分 LMM | **是，输出质量/美学等级概率** | **是，为视觉评分训练** | **有质量/美学问题模板** |
| **WISE / WiScore** | **机评** | 通用 MLLM judge | **是** | 通常不为 WISE 单独微调 | **有详细评价 rubric** |
| **Vendi Score** | **机评** | 图像 embedding + 数学计算 | **否** | 不为 Vendi 专门微调 | **无** |
| **GEdit-Bench / VIEScore** | **机评** | 通用 MLLM；GPT-4.1 或 Qwen2.5-VL-72B 等 | **是，分别评 SC/PQ** | VIEScore 本身主要是提示词框架，不为 GEdit 专门微调 | **有 SC 与 PQ 评价模板** |
| **背景 PSNR/SSIM** | **机评** | 传统算法 | **否** | **否，无模型** | **无** |
| **背景 LPIPS** | **机评** | 学习的感知相似度模型 | **否** | **是，为感知相似度学习**；不是 VLM judge | **无** |
| **DINO-I** | **机评** | 自监督视觉 embedding | **否** | 不为当前主体评测微调 | **无** |
| **CLIP-I** | **机评** | CLIP 图像 embedding | **否，仅图像—图像** | 不为当前主体评测微调 | **无文本提示词** |
| **DreamBench++ CP/PF** | **机评** | 通用 GPT-4o judge | **是** | 不为 DreamBench++ 单独微调 | **有 CP、PF 两套 0–4 评价指令** |
| **MMIG-AMS** | **机评** | Qwen2.5-VL-72B VQA | **是，回答 aspect QA** | 不为 AMS 单独微调 | **有预生成 aspect QA** |
| **人工成对胜率 / 人工 PQ** | **人评** | 人类评审者 | **否** | 不适用 | 有人评说明和 rubric，但不是 AI 提示词 |

> **机评**：由 AI 模型或传统算法自动评分，包括 VLM、微调奖励模型、OCR、embedding 和 PSNR/SSIM 等。**人评**：本次评测由人类评审者对输出图打分、排序或投票。使用人工标注数据训练，不会把机评自动变成人评。

> “使用人类偏好数据训练”与“使用通用 VLM 按提示词评审”是两种不同路线。HPS v3 属于前者；GEdit、WISE、DreamBench++ 属于后者。

---

## 三、哪些有固定问题，哪些真的让 VLM 打分？

### 1. 固定 VQA 问题：Soft-TIFA、DPG、MMIG-AMS

这类方法通常不直接问“请打几分”，而是预先准备可验证的问题。

#### Soft-TIFA 示例

生图 prompt：

> four white bicycles in front of three plastic cows

数据中的问题形式类似：

```text
How many bicycles are in the image?       → four
Are the bicycles white?                  → Yes
Are there any bicycles in the image?     → Yes
Are the bicycles in front of the cows?   → Yes
How many cows are in the image?          → three
Are the cows plastic?                    → Yes
```

评分器回答后，取**正确答案概率**，再计算 AM/GM。

#### DPG 示例

```text
Is there a coffee shop on the left side of the street?
Is the girl wearing a red raincoat?
Is the bicycle blue?
Is the girl standing to the right of the coffee shop?
```

#### MMIG-AMS 示例

```text
Does the image contain the same black backpack as the reference image?
Is the backpack on the left of the white shoes?
Does the top text read "URBAN DAILY"?
```

这些问题的质量、依赖关系和答案规范化，比临时写一段“请全面评价”更关键。

### 2. 直接让 VLM 输出分数：WISE、GEdit、DreamBench++

这类方法有明确评分量表和 rubric。VLM 自报的 8 分是**语言模型输出**，不是由固定检测规则直接得到的真值。

### 3. 折中形式：VQAScore、Q-Align

- VQAScore 问一个固定 Yes/No 问题，但保留 **Yes 概率**作为连续分。
- Q-Align 让模型在五个质量词上输出概率，再加权成连续分。

---

## 四、提示词示例

### 1. VQAScore：官方经典问法

```text
Does this figure show "{prompt}"? Please answer yes or no.
```

答案目标：

```text
Yes
```

计算：

```text
VQAScore = P("Yes" | image, question)
```

它不是让模型输出“8.7 分”，也不是让模型自由解释后再主观换算。

### 2. Q-Align：质量评分问题

常见形式为：

```text
Can you rate the quality of this picture?
```

回答前缀形式类似：

```text
The quality of the image is
```

模型在以下词上形成概率：

```text
excellent / good / fair / poor / bad
```

再加权为 5、4、3、2、1 的期望分。**具体措辞应以所用 Q-Align/OneAlign checkpoint 的官方代码为准。**

### 3. GEdit / VIEScore：SC 与 PQ 分开问

下面是**理解用简化示意**，不是官方逐字模板。

#### SC：语义一致性

```text
You are evaluating an instruction-guided image edit.

Editing instruction:
{instruction}

Inputs:
1. Source image
2. Edited image

Evaluate:
- Whether the requested edit has been completed.
- Whether content that should remain unchanged has been preserved.

Give a semantic consistency score from 0 to 10.
Return a short rationale and the score in the required format.
```

#### PQ：感知质量

```text
Evaluate the perceptual quality of the edited image alone.

Focus on:
- Naturalness
- Visual artifacts
- Distorted structures
- Blending quality

Do not score whether the edit instruction was followed.
Give a perceptual quality score from 0 to 10.
```

随后由程序计算：

```text
Overall = sqrt(SC × PQ)
```

不要让同一个问题同时混问 SC 和 PQ，否则容易失去维度解耦。

### 4. WISE：知识与三维评分

下面是**原版逻辑的理解用简化示意**：

```text
You are evaluating an image generated from a knowledge-informed prompt.

Prompt:
{prompt}

Required world knowledge and expected meaning:
{explanation}

Evaluate three aspects independently:
1. Consistency: Does the image realize the required knowledge and relations?
2. Realism: Is the image believable and realistic?
3. Aesthetic quality: Is the image visually appealing?

Assign each aspect an integer score of 0, 1, or 2.
Return the three scores in the specified format.
```

程序再计算：

```text
WiScore = (0.7×Consistency + 0.2×Realism + 0.1×Aesthetic) / 2
```

**WISE_Verified 不使用这套三维分**，而是让指定 Qwen judge 判断知识含义、关键关系和视觉可用性是否整体满足，输出二值 0/1。两版提示词不可混用。

### 5. DreamBench++：CP 与 PF 分开问

以下为**理解用简化示意**。

#### Concept Preservation（0–4）

```text
Compare the reference image and the generated image.

Evaluate whether the specific concept or subject is preserved.
Focus on shape, color, texture, and facial features when applicable.

Use this scale:
0 = very poor
1 = poor
2 = fair
3 = good
4 = excellent

Return the concept preservation score and rationale.
```

#### Prompt Following（0–4）

```text
Compare the target prompt and the generated image.

Evaluate relevance, accuracy, completeness, and context.
Do not award prompt-following points merely for preserving the reference image.

Return a score from 0 to 4 and a rationale.
```

官方流程还包括任务理解、总结和规划等 self-alignment 设计；复现时应使用官方完整模板。

### 6. HPS v3：为什么没有 judge 提示词示例？

HPS v3 的输入是：

```text
generation prompt + generated image
```

经过微调后的 Qwen2-VL 和奖励头输出：

```text
μ, σ
```

它不需要下面这种指令：

```text
Please rate this image from 0 to 10.
```

因此不能把它与 GEdit 的 prompt-based judge 混为一类。生图 prompt 是评价条件，不是评审指令。

---

## 五、实际选择建议

| 需求 | 更合适的方法类型 |
|---|---|
| 希望逐项验证对象、数量、属性、关系 | 固定 QA 的 Soft-TIFA、DPG、MMIG-AMS |
| 希望在私有 prompt 上快速得到连续语义分 | VQAScore |
| 希望评价开放编辑、知识或个性化，缺少固定规则 | 通用 VLM rubric：GEdit、WISE、DreamBench++ |
| 希望低成本批量预测人类综合偏好 | 微调奖励模型：HPS v3 等 |
| 希望专门评感知质量/美学等级 | 微调评分模型：Q-Align/OneAlign |
| 希望结果完全不依赖 VLM 语言判断 | OCR、PSNR/SSIM、LPIPS、DINO-I、CLIP-I、Vendi |
| 希望最终验证用户真实选择 | 人工成对盲测，而不是继续增加 VLM judge |

## 六、复现时必须保存的内容

- 评审器类型：通用 VLM、微调奖励模型、专用模型或传统算法；
- 模型 ID、checkpoint、revision 和运行日期；
- 完整评价提示词或固定 QA 文件；
- 图像输入顺序、分辨率和预处理；
- temperature、top-p、最大输出长度；
- 原始回答、答案概率和解析后的分数；
- 算术公式与聚合方式。

**只写“使用 Qwen/GPT 评分”远远不够。** 同一个模型换一套提示词，就可能成为另一种评价协议。
