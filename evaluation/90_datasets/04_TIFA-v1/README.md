# TIFA v1.0 / TIFA-160

## 数据卡

- **任务**：细粒度文图忠实度及自动评分器人机相关验证。
- **TIFA v1.0**：约 **4,000 条文本、2.5 万个预生成 QA**，文本来源包括 COCO、DrawBench、PartiPrompts 等。
- **TIFA-160**：160 条 prompt 的常用人工标注子集；原 TIFA 提供每图人工忠实度评分，DSG 另发布更密集的每图 5 份 Likert 标注版本。
- **标注内容**：prompt、问题、标准答案、题型/元素类别、图像路径映射；官方 QA 已生成，无需再次调用 LLM。

## 适合指标

[TIFA](../../01_alignment/04_TIFA/) 为主，也可在同一批图上比较 CLIPScore、VQAScore、DSG 与 Soft-TIFA，并用 SRCC/KRCC/成对准确率验证人机一致性。

## 版本坑

用 GPT-3.5 重新生成的问题与 v1.0 预生成问题不完全相同；换 mPLUG-large 为其他 VQA 也形成新协议。TIFA-160 的人工相关结果不能自动推广到所有 4,000 条或新一代模型。

## 来源

- 论文：[TIFA, ICCV 2023](https://arxiv.org/abs/2303.11897)
- 官方 QA、prompt、图像与人工标注入口：[Yushi-Hu/tifa](https://github.com/Yushi-Hu/tifa)
- DSG 的 TIFA-160 扩展标注：[j-min/DSG](https://github.com/j-min/DSG)
