# DSG-1k

## 数据卡

- **任务**：依赖感知、原子化的细粒度文图对齐。
- **规模**：**1,060 条 prompt**，名称中的 1k 不是精确条数。
- **八类**：TIFA 160、paragraph 200、relation 100、count 100、real_user 200、pose 100、defying 100、text 100。
- **标注**：PaLM 2 等预生成的原子 yes/no 问题、语义 tuples 与 parent dependency；另发布多 VQA 模型的示例回答。

## 适合指标

[DSG](../../01_alignment/05_DSG/) 及 VQA 类方法。可将同批生成图用于 TIFA/VQAScore/Soft-TIFA 对照，但必须遵循各方法自己的聚合规则。

## 优点与局限

覆盖长段落、真实用户文本、关系、计数、姿态、反常场景和文字，问题图提供可解释性。局限是 QG/VQA 误差、问题二值化和多问题推理成本；text 类 100 条不能代替完整 OCR 基准。

## 复现必填

`dsg-1k-anns.csv版本 / VQA checkpoint / 父级归零规则 / 每prompt图数 / 八类分项与宏微平均`。

## 来源

- 论文：[Davidsonian Scene Graph, ICLR 2024](https://arxiv.org/abs/2310.18235)
- 官方数据与代码：[j-min/DSG](https://github.com/j-min/DSG)
