# MS COCO / COCO Captions（评测用途）

## 数据卡

- **任务**：真实图像参考分布、图文对齐、通用 prompt 来源。
- **相关 split**：COCO 2014 validation 有 **40,504 张图**；COCO Captions 通常每图 5 条人工描述。Karpathy split 另将数据划为 train/val/test，不能与普通 val2014 混称。
- **常见生成协议**：从验证 caption 中抽样约 30k prompt，生成一图/prompt，与 COCO val 图像计算 FID/CMMD；具体抽样列表决定可复现性。
- **标注**：图像、实例/分割等多类 COCO 标注及 captions；不同标注文件许可与用途需分别核对。

## 适合指标

[FID](../../04_distribution/02_FID/)、[CMMD](../../04_distribution/04_CMMD/)、CLIPScore、VQAScore，以及 GenEval 的检测器基础。FID/CMMD 只用图像分布，不验证 caption 对齐；必须另加语义指标。

## 局限

COCO 是 2014 年自然照片域，分辨率、题材、构图和文字覆盖与当代海报/艺术/高分辨率生成不同。CMMD 官方也提醒 COCO val 分辨率偏低，不足以评价 1024×1024 生成的全部细节。

## 复现必填

`prompt文件及哈希 / caption选择规则 / N / real split / resize / seed / 实现版本`。不要写“COCO FID=…”却没有这六项。

## 来源

- 官方数据：[COCO download](https://cocodataset.org/#download)
- Lin et al., **Microsoft COCO: Common Objects in Context**：[论文](https://arxiv.org/abs/1405.0312)
- Chen et al., **Microsoft COCO Captions**：[论文](https://arxiv.org/abs/1504.00325)
