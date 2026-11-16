# TextAtlasEval / TextAtlas5MEval

## 数据卡

- **任务**：长文本、稠密文字图像生成。
- **评测规模**：官方从 TextAtlas5M 各子集分层抽样约 **3,000 个评测样本**；具体子集和版本以官方脚本为准。
- **内容**：StyledTextSynth、TextScenesHQ、TextVisionBlend 等来源，覆盖合成文字、真实场景和图文混合排版。
- **训练集**：TextAtlas5M 是大规模稠密文字数据集，不能与 3k 评测集混称。

## 常用指标

FID、CLIPScore、OCR Accuracy/F1、CER 等。长文本建议使用 micro CER、整图完全正确率和 OCR-F1，避免“每行大部分字对”掩盖整页不可用。

## 优点与局限

补足早期基准只有短词/短句的缺口，适合测试长上下文规划与排版；但合成长文本与真实用户海报有域差，OCR 对稠密小字本身也更易错，需控制分辨率并人工抽检。

## 来源

- 项目与数据：[TextAtlas5M](https://textatlas5m.github.io/)
- **TextAtlas5M: A Large-scale Dataset for Dense Text Image Generation**（以项目页论文链接为准）
