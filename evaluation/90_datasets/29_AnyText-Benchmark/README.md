# AnyText-Benchmark / AnyWord-3M

## 数据卡

- **任务**：多语言视觉文字生成与编辑。
- **AnyText-Benchmark**：**1,000 张英文 + 1,000 张中文**基准图，分别来自 LAION 与 Wukong 等来源。
- **训练数据**：AnyWord-3M，约 300 万图文样本，带多语言 OCR 标注；训练集与 benchmark 不可混称。
- **内容**：目标文字、位置/区域和源图等，支持文字生成及编辑。

## 官方常用指标

- **Sentence Accuracy**：整句 exact match，越高越好；
- **NED**：编辑距离相似度，越高越好；
- **FID**：整体图像分布质量，越低越好。

## 复现注意

OCR 引擎、语言、文本归一化、框匹配和 FID 参考集必须固定。后续工作可能使用清洗后的不同子集，因此同一“AnyText benchmark”下数字也可能不同；报告实际评测列表。FID 不证明文字正确。

## 来源

- Tuo et al., **AnyText: Multilingual Visual Text Generation and Editing**：[论文](https://arxiv.org/abs/2311.03054)
- 官方代码与数据入口：[tyxsspa/AnyText](https://github.com/tyxsspa/AnyText)
