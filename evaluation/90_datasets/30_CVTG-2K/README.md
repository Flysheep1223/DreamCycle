# CVTG-2K（Complex Visual Text Generation）

## 数据卡

- **任务**：复杂场景、多区域视觉文字生成。
- **规模**：**2,000 条 prompt**。
- **场景**：街景、书封、广告、海报、便签、meme、Logo、电影画面等。
- **难点**：每条可含 **2–5 个文字区域**，并要求指定区域内容、位置/载体；平均文字长度高于许多早期基准。
- **属性**：部分样本指定文字大小、颜色和字体等。

## 适合指标

OCR Sentence Accuracy、NED、CER/WER、端到端 OCR-F1；另报每区域完全正确和整图全部区域正确。位置/字体/颜色应另设布局与属性评价，FID/CLIPScore 只作图像辅助。

## 优点与局限

多区域和属性约束比单句文字 benchmark 更接近海报生产，但 OCR 的区域匹配、阅读顺序和文字归一化会显著影响结果。不能只报告检出文本平均相似度而忽略漏区域和额外幻觉文字。

## 来源

- **TextCrafter: Accurate Rendering of Multiple Texts in Complex Visual Scenes**：[论文](https://arxiv.org/abs/2503.23461)
- 项目页：[dnknju.github.io/textcrafter-site](https://dnknju.github.io/textcrafter-site/)
