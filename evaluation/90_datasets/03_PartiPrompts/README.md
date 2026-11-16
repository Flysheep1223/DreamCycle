# PartiPrompts（P²）

## 数据卡

- **任务**：通用文生图能力和挑战维度分析。
- **规模**：**1,600 条英文 prompt**。
- **组织**：同时按内容类别与 challenge 维度组织，覆盖抽象、知识/推理、精细细节、文字、视角、风格等。
- **形式**：公开 prompt 表，不提供唯一正确生成图。

## 适合指标

人工偏好/MOS、CLIPScore、VQAScore、TIFA、DSG、VIEScore，以及 HPS/PickScore 等偏好分。DPG-Bench 的部分长 prompt 构建也参考了 PartiPrompts。

## 优点与局限

挑战标签使其比随机 COCO caption 更适合发现模型弱点，且规模足以做分片分析；但标签稀疏程度、模板化 prompt 和公开长期使用会造成覆盖/泄漏问题。单一 overall 会掩盖不同 challenge 的难度和样本数。

## 推荐协议

按官方 category/challenge 分层报告，固定每 prompt 图数。不要把“同一 prompt 多标签”当成重复独立样本；区间估计以 prompt 为聚类单位。

## 来源

- Yu et al., **Scaling Autoregressive Models for Content-Rich Text-to-Image Generation (Parti)**：[论文](https://arxiv.org/abs/2206.10789)
- 官方项目：[parti.research.google](https://parti.research.google/)
- 官方仓库：[google-research/parti](https://github.com/google-research/parti)
