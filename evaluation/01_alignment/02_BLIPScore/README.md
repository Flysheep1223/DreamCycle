# BLIPScore / BLIP-ITC / BLIP-ITM

## 一句话介绍

“BLIPScore”不是完全唯一的标准名称：实践中有用 BLIP 双编码器的图文余弦（ITC），也有用 BLIP 融合编码器的图文匹配概率（ITM）。写报告时必须展开具体计算，不能只写 BLIPScore。

- **输入**：图像与 prompt
- **输出**：ITC 为相似度；ITM 常为匹配类别概率/logit，越高越好
- **参考自由**：是
- **适用**：整体语义基线、同 prompt 排序；不是专门的组合正确率

## 两种计算方式

### 1. BLIP-ITC / cosine 形式

BLIP 的 image-grounded text 架构提供单模态图像与文本表示。归一化后：

`S_ITC = cos(E_img(x), E_txt(p))`

有些论文把它乘 100，有些直接使用。不同 BLIP/BLIP-2 backbone、特征层和缩放不能混比。

### 2. BLIP-ITM 形式

图像和文本经跨注意力融合，二分类头判断匹配/不匹配：

`S_ITM = P(match | x,p) = exp(l_match)/(exp(l_match)+exp(l_mismatch))`

ITM 比单向 cosine 多了跨模态交互，通常计算更重。若使用原始二分类 logit 而不是 softmax 概率，应明确其无界、非概率的性质。

## 评分流程

1. 固定 BLIP 版本（例如 BLIP base/large、BLIP-2 变体）和预训练权重。
2. 使用模型要求的图像预处理与文本 tokenizer。
3. 明确选择 ITC 特征 cosine、ITM 正类概率或正类 logit。
4. 对同 prompt 候选图排序，或对 benchmark 样本求均值；保存逐样本值。

## 数据与验证

BLIP 原始工作主要面向视觉语言预训练、检索、描述和 VQA，不是文生图专用人工偏好数据。用于生成评测时可在 TIFA-160、GenAI-Bench 或带人工对齐标签的数据上验证 SRCC/成对准确率，但应单独报告验证结果，不能把检索性能当成生成评测可靠性。

## 优点

- ITC 推理轻量，ITM 提供比独立向量更直接的跨模态交互。
- 开源生态成熟，可作为 CLIP 之外的第二视觉语言表示。
- 可解释到输入图文对，不需要真实参考图。

## 局限

- 与 CLIP 类似，对对象数量、属性绑定、关系、否定和视觉文字可能失灵。
- “BLIPScore”在不同论文中可能指不同模型/头，绝对值与排序都未必一致。
- BLIP 与 ImageReward 不同：**ImageReward 是在 BLIP 骨干上用生成图人类偏好监督训练的奖励模型**，不能把普通 BLIP 匹配分称为 ImageReward。
- ITM 的概率是训练分布内的匹配置信度，不等于“prompt 所有条件成立”的真实概率。

## 推荐报告格式

写为：`BLIP-2-ITM (checkpoint=..., P(match), prompt_set=..., macro mean)`，而不是单独写 `BLIP=0.83`。若只需要快速粗筛，优先固定一种实现并补充 VQAScore/Soft-TIFA。

## 来源

- Li et al., **BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation**, ICML 2022：[论文](https://arxiv.org/abs/2201.12086)
- Li et al., **BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models**, ICML 2023：[论文](https://arxiv.org/abs/2301.12597)
- 官方代码：[salesforce/BLIP](https://github.com/salesforce/BLIP)、[salesforce/LAVIS](https://github.com/salesforce/LAVIS)
