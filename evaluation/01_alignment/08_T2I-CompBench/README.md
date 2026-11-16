# T2I-CompBench / T2I-CompBench++

## 一句话介绍

面向开放世界组合生成的**多评测器基准套件**：不同语义类型分别用 BLIP-VQA、UniDet、CLIP 或 MLLM，避免指望一种模型可靠判断所有组合能力。

- **T2I-CompBench**：NeurIPS 2023，原版 6,000 条 prompt。
- **T2I-CompBench++**：TPAMI 2025，扩展到 **8,000 条 prompt、4 大类、8 个子类**。
- **输出**：各子任务分别报告，通常为 0–1 的匹配/正确分，越高越好；不是天然统一的一个标量。

## 任务与评测器

| 能力 | 子类 | 官方主要评分方法 |
|---|---|---|
| Attribute binding | color、shape、texture | Disentangled BLIP-VQA，分别问对象与属性，减少绑定歧义 |
| Object relationships | 2D spatial、3D spatial、non-spatial | 2D/3D 用 UniDet 检测，3D 还结合深度；非空间原版用 CLIP，++ 增加 MLLM 评价 |
| Generative numeracy | 数量 | UniDet 检测对象并计数 |
| Complex compositions | 多对象、多属性、多关系 | 原版 3-in-1 综合评分；++ 提供 GPT-4V/ShareGPT4V 等 MLLM 路线 |

“Disentangled”关键不是只问整句是否匹配，而是将对象存在、属性及归属拆开检查。例如“绿长凳与蓝碗”应分别验证两个对象及各自颜色，避免全图有绿和蓝就通过。

## 通用流程

1. 按子类 prompt 文件生成图像；官方历史推理示例曾使用每 prompt 10 张和固定 seed，复现某张表时必须遵循对应版本。
2. 属性任务运行 BLIP-VQA；空间与计数运行 UniDet 及相应深度/规则代码。
3. 非空间/复杂组合按原版或 ++ 选择 CLIP、3-in-1 或指定 MLLM。
4. 保存每个问题的连续分/判断，再按官方脚本对子任务聚合。
5. 若需要 overall，明确是八类等权宏平均还是其他口径；优先展示完整分项，不自行创造不可比总分。

## 优点

- 覆盖颜色/形状/纹理绑定、2D/3D 空间、非空间关系、数量及复杂组合，诊断性强。
- 对适合规则验证的任务使用检测器，对复杂语义引入 VQA/MLLM，比全任务只用 CLIP 更合理。
- 开放 prompt 与代码，被多种生成模型论文采用，历史可比资料较多。

## 局限

- 不同子任务评分器的尺度与误差不同，直接平均不一定有统一语义。
- 检测器对开放类别、艺术风格、遮挡和异常构图可能失效；深度估计也会引入误差。
- MLLM 结果受模型版本、提示词、温度和采样影响；GPT-4V 等旧接口复现困难。
- 原版与 ++ 的数据规模、评分器和生成协议不同，跨表比较必须核对版本。
- 组合对齐高并不表示画质、美感或偏好高。

## 推荐实践

- 技术报告至少给八个子类，不只给 overall。
- 同批图可补 VQAScore/Soft-TIFA，验证检测器或 MLLM 的盲区和漂移。
- 对绑定错误构造“交换属性”反例，对空间构造左右/前后反转，对数量构造 ±1，做评分器灵敏度测试。
- 记录每 prompt 图数；best-of-10 与 10 张平均代表完全不同产品能力。

## 官方来源

- Huang et al., **T2I-CompBench**, NeurIPS 2023：[论文](https://arxiv.org/abs/2307.06350)
- Huang et al., **T2I-CompBench++**, TPAMI 2025：[DOI](https://doi.org/10.1109/TPAMI.2025.3531907)
- 项目页：[T2I-CompBench-new](https://karine-h.github.io/T2I-CompBench-new/)
- 官方代码与数据入口：[Karine-Huang/T2I-CompBench](https://github.com/Karine-Huang/T2I-CompBench)（仓库说明文件名为 `Readme.md`）
