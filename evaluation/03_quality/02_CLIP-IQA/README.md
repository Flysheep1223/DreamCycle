# CLIP-IQA / CLIP-IQA+

## 一句话介绍

把图像与一对反义提示词（如 “Good photo.” / “Bad photo.”）分别计算 CLIP 相似度，再用 softmax 得到图像属于正向属性的概率，实现免参考质量与观感评分。

- **输入**：单张图，无需 prompt 或参考图
- **输出**：0–1，越高表示越接近正向提示
- **可测属性**：质量、亮度、噪声、色彩、清晰度、对比度、自然/合成、快乐/悲伤等
- **CLIP-IQA+**：在原方法基础上引入任务数据训练/提示学习，不再是完全零样本

## 基本公式

设图像 embedding 为 `v`，正、负提示 embedding 为 `t+`、`t-`：

`p+ = exp(cos(v,t+)) / [exp(cos(v,t+)) + exp(cos(v,t-))]`

`CLIP-IQA = p+`

有些实现使用温度参数或先乘缩放，必须遵循具体实现。两个提示共享大部分句子、只替换反义词，可以减少无关语言差异。

常见配对：

- quality：Good photo / Bad photo
- sharpness：Sharp photo / Blurry photo
- noisiness：Clean photo / Noisy photo
- natural：Natural photo / Synthetic photo
- beautiful：Beautiful photo / Ugly photo

“natural”与“beautiful”测的是不同属性，不应混为一个画质分。

## 评分流程

1. 固定 CLIP backbone 和官方/实现自带 prompt pairs。
2. 编码图像及正反提示，计算 softmax 正类概率。
3. 分属性报告，不按未经验证的权重求总分。
4. 在带人工 MOS 的生成图数据上计算 SRCC/PLCC，验证该属性是否适合当前模型域。

## 优点

- 无需人工参考图，也无需为每个新数据集重新训练基础版。
- 同一框架能评估技术质量与更主观的 look-and-feel 属性。
- 正反提示相对直观，能解释分数来自哪一种语义属性。
- 轻量，可与 CLIPScore 共用部分基础设施。

## 局限

- 本质是 CLIP 文本语义分类，不是精确的失真测量；细微伪影、手部异常和拼写错误可能漏检。
- 提示词、backbone 和温度会显著影响校准，0.8 不是“80% 人认为好”。
- 自然照片 IQA 上有效不代表生成图域同样可靠；需要用 AGIQA-3K 等生成图人工数据验证。
- “Natural/Synthetic”可能把合理的插画风格判成低质量，不应拿它统一惩罚非写实生成。
- CLIP-IQA+ 使用训练数据后，训练/测试域和分数不能与零样本 CLIP-IQA 混用。

## 官方来源与实现

- Wang, Chan, Loy, **Exploring CLIP for Assessing the Look and Feel of Images**, AAAI 2023：[论文](https://arxiv.org/abs/2207.12396)
- 官方代码：[IceClear/CLIP-IQA](https://github.com/IceClear/CLIP-IQA)
- 易用实现：[TorchMetrics CLIP-IQA](https://torchmetrics.readthedocs.io/en/stable/multimodal/clip_iqa.html)、[IQA-PyTorch](https://github.com/chaofengc/IQA-PyTorch)

> 报告示例：`CLIP-IQA / clip_iqa checkpoint / quality prompt pair / mean p+`；若使用多个属性，逐列展示。
