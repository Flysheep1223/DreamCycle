# DreamBench++（CP / PF）

## 一句话介绍

面向个性化/主体驱动生成的人工对齐基准，用 GPT-4o 分别评价 **Concept Preservation（概念/主体保持，CP）** 与 **Prompt Following（文本遵循，PF）**，强调两者的 Pareto 平衡。

- **数据**：150 张参考图、1,350 条 prompt（每图 9 条）
- **prompt 构成**：4 条写实、3 条非写实、2 条复杂/想象性
- **评分**：0–4 整数，0 very poor、4 excellent；CP 与 PF 分别报告
- **原始 judge**：GPT-4o，含任务强化与 self-alignment 设计

## 两个维度

### Concept Preservation（CP）

比较参考图和生成图，关注 shape、color、texture，以及人物适用时的 facial features。目标是保留“这个特定主体/风格”，不是只生成同类别对象。

### Prompt Following（PF）

比较目标 prompt 与生成图，关注 relevance、accuracy、completeness、context。目标是在新姿态、新场景、新风格中完成文本要求。

模型可能复制参考图而 CP 高、PF 低，也可能完全重画而 PF 高、CP 低；因此不应只报其中一个。

## GPT 评审流程

1. 给出任务说明、维度专用评分准则、0–4 定义与输出格式。
2. 让模型先确认理解并总结任务（internal thinking）。
3. 让模型总结和规划评分（summary & planning）。
4. 输出 CP 或 PF 数值及必要理由。
5. 在测试集按人/动物/物体/风格和 prompt 难度聚合，观察 CP–PF Pareto。

作者选择绝对 rating 而非所有模型两两比较，一部分原因是 GPT 图像顺序位置偏差和成对比较随模型数二次增长。绝对评分仍需检测 judge 漂移和尺度压缩。

## 相比 DreamBench

DreamBench 原始为 30 个 subject、25 条 prompt，并常用 DINO/CLIP-I/CLIP-T。DreamBench++ 扩展到 150 张参考图、1,350 prompt，增加人物、物体与非自然风格多样性，并用人工对齐的 MLLM 评分补足 CLIP/DINO 对细节身份特征不敏感的问题。

## 优点

- 同一协议同时覆盖“像不像同一主体”和“听不听话”。
- 数据与 prompt 类型更丰富，人物和复杂想象场景更有挑战。
- 0–4 rubric 与评审 prompt 公开，较易审计和人工复核。
- Pareto 视角避免只优化复制相似度。

## 局限

- 商业 GPT-4o 成本、快照与输出波动影响复现；换 MLLM 后需要重新验证人类一致性。
- CP/PF 仍有 judge 主观性，尤其风格保持与合理创作自由的边界。
- 0–4 等级较粗，可能难以区分细微身份差异；多 seed 方差也需单独考虑。
- 总平均会掩盖人物、物体、风格等类别差异，不建议只报一个 CP+PF 总分。

## 官方来源

- Peng et al., **DreamBench++: A Human-Aligned Benchmark for Personalized Image Generation**, ICLR 2025：[论文](https://arxiv.org/abs/2406.16855)
- 项目页：[dreambenchplus.github.io](https://dreambenchplus.github.io/)
- 官方代码：[yuangpeng/dreambench_plus](https://github.com/yuangpeng/dreambench_plus)
