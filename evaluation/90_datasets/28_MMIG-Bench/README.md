# MMIG-Bench 数据集

## 数据卡

- **任务**：纯文本与多模态图像条件生成的统一评价。
- **规模**：**4,850 条富标注 prompt、1,750 张多视角参考图、380 个 subject**。
- **主体**：人物、动物、物体、艺术风格。
- **标注**：prompt aspect phrases 与相应 VQA QA pairs，涵盖对象、属性、关系、计数等；人工验证约 32.4k ratings。

## 适合指标

[MMIG 三层套件与 AMS](../../06_editing_multimodal/06_MMIG-Bench/)：低层 CLIP-T、CLIP-I、DINOv2、CUTE、PAL4VST；中层 Qwen2.5-VL-72B AMS；高层 Aesthetic/HPSv2/PickScore。

## 优点与局限

同时检验组合语义、身份保持、伪影和偏好，特别适合多参考、多视角生成。使用时需区分 text-only 与 image+text 子集，不能把两套总体直接混算；参考人物/图像需遵守许可与隐私要求。

## 来源

- Hua et al., **MMIG-Bench**, NeurIPS 2025：[论文](https://arxiv.org/abs/2505.19415)
- 官方代码：[hanghuacs/MMIG-Bench](https://github.com/hanghuacs/MMIG-Bench)
- 数据：[hhua2/MMIG-Bench](https://huggingface.co/datasets/hhua2/MMIG-Bench)
