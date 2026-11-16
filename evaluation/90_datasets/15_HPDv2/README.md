# HPD v2（Human Preference Dataset v2）

## 数据卡

- **任务**：文生图人类偏好训练、验证与固定风格 benchmark。
- **规模**：约 **798k 次偏好选择、430k+ 张图、107k 条 prompt**。
- **split**：官方 README 约 **645k train pairs / 153k test pairs**。
- **来源**：多个文生图模型与 COCO Captions；prompt 来自 DiffusionDB 与 MSCOCO，DiffusionDB prompt 经清理。
- **测试标注**：可含每图平均 rank 与逐标注者 `raw_annotations`。

## 适合指标

[HPS v2/v2.1](../../02_preference/02_HPSv2/) 训练与偏好准确率验证，也可外部测试 PickScore、ImageReward、MPS、HPSv3。官方另有 Animation、Concept-art、Painting、Photo 四类固定 benchmark prompts。

## 规模常见误写

430k 是图像量级，不是“433,760 个图像对”；798k 是偏好选择，不是独立 prompt。v2.0 与 v2.1 模型分也不能直接比较。

## 来源

- 论文：[Human Preference Score v2](https://arxiv.org/abs/2306.09341)
- 官方代码：[tgxs002/HPSv2](https://github.com/tgxs002/HPSv2)
- 数据：[ymhao/HPDv2](https://huggingface.co/datasets/ymhao/HPDv2)
