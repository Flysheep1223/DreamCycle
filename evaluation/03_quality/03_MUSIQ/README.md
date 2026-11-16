# MUSIQ（Multi-scale Image Quality Transformer）

## 一句话介绍

用多尺度图像 patch 表示与 Transformer 在原生分辨率上做无参考图像质量评价，避免把所有输入强行 resize/crop 到固定小尺寸。

- **输入**：单张图
- **输出**：学习到的质量/美学回归分，越高越好；具体尺度由 checkpoint 训练标签决定
- **是否需要 prompt**：否
- **常见训练数据**：PaQ-2-PiQ、KonIQ-10k、SPAQ、AVA

## 方法原理

传统 IQA 常将图像缩放到 224×224，可能抹掉压缩噪声、模糊和高频伪影。MUSIQ：

1. 保留原生分辨率，构建多尺度 patch；
2. 将 patch 位置、尺度等信息编码进 Transformer；
3. 聚合整图信息，输出质量分。

因此它适合评估不同长宽比和高分辨率图像，但计算与显存会随分辨率/patch 数变化。

## 分数为什么不能跨 checkpoint 比较

- PaQ-2-PiQ 等 MOS 训练的分常落在约 0–100 的范围；
- AVA 训练更偏摄影美学，标签尺度不同；
- KonIQ/SPAQ 等各自 MOS 分布也不同。

“MUSIQ=65”只有在指定 checkpoint、预处理和训练集时才有意义。AVA 版不应被当作 PaQ-2-PiQ 技术画质版。

## 配套数据

- **PaQ-2-PiQ**：约 40k 整图、120k patch 与大量人类质量判断，强调从局部到整图质量。
- **KonIQ-10k / SPAQ**：真实自然图像质量及 MOS，主要仍不是 AI 生成图专用。
- **AVA**：美学评价而非纯失真质量。
- 对生成图可另在 AGIQA-3K、AIGCIQA 等人工标注集上做人机相关验证。

## 优点

- 原生分辨率、多尺度，对细节失真比固定 resize 的方法更有优势。
- 不需要参考图或文本，适合批量筛图。
- 多个公开 checkpoint 与 PyTorch 复现，使用成熟。

## 局限

- 训练 MOS 多来自自然摄影，对生成图的手部、结构、语义幻觉和文字错误没有专门保证。
- 不知道 prompt，无法评价漏对象、错关系或编辑失败。
- 高分辨率原生输入会增加成本；不同实现对长边、patch 数的限制也可能不同。
- 不同训练数据/checkpoint 的数值不可直接比较，也不宜与 Aesthetic Score 直接换算。
- 高分不表示图像一定受目标用户喜欢。

## 官方来源与实现

- Ke et al., **MUSIQ: Multi-scale Image Quality Transformer**, ICCV 2021：[论文](https://arxiv.org/abs/2108.05997)
- 官方代码：[google-research/google-research/musiq](https://github.com/google-research/google-research/tree/master/musiq)
- PyTorch 工具箱：[chaofengc/IQA-PyTorch](https://github.com/chaofengc/IQA-PyTorch)

```python
import pyiqa
metric = pyiqa.create_metric("musiq", device="cuda")  # 仍应打印/记录实际权重
score = metric("image.png")
```
