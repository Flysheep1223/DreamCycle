# 指令编辑：GEdit-Bench 的 SC、PQ、Overall

## 1. 这个维度测什么？

图像编辑不是“生成一张漂亮图”就够了，还要同时满足：

- 指定修改是否完成；
- 指令要求保持的内容是否保持；
- 修改后是否自然、无明显伪影。

GEdit-Bench 用 606 个真实用户编辑实例、11 类任务和中英文指令，让 MLLM 输出：

- **SC（Semantic Consistency）**：语义一致性；
- **PQ（Perceptual Quality）**：感知质量；
- **O（Overall）**：单图 `√(SC×PQ)`。

三者通常均为 0–10，越高越好。

## 2. 完整例子

源图：一位没有佩戴项链的人物，背景是书店。

指令：

> 给人物增加一条红宝石吊坠项链，其他内容保持不变。

假设 judge 给出：

| 输出 | 实际表现 | SC | PQ | O=√(SC×PQ) |
|---|---|---:|---:|---:|
| A | 加上合适项链，人物和书店基本保持 | 9 | 8 | **8.49** |
| B | 加上项链，但换了脸并大幅改变背景 | 4 | 9 | **6.00** |
| C | 几乎原图直出，没有项链 | 1 | 9 | **3.00** |

解释：

- A 两者均衡，Overall 最高；
- B 画质高，但没有满足“其他内容保持不变”；
- C 说明**高 PQ 不能弥补编辑失败**。

这些 judge 分数是演示值，不是 GEdit 官方结果。

## 3. 任务宏平均示例

官方统计代码先在每类任务内求平均，再对 11 类等权平均。若只为演示，模型在两类上的 O 分别为：

- subject-add：8.2；
- background_change：5.6。

如果其他九类都为 7.0，则：

`Overall = (8.2+5.6+9×7.0)/11 ≈ 6.98`

它不是把所有图混在一起后按各类样本数加权，因此小类也有同等影响力。

## 4. Full set 与 Intersection：保持效果比较样本一致

本指南只评价输出图像的编辑效果，不讨论服务可用性。比较不同模型时，应使用相同的样本范围并公开样本列表，避免在不同难易程度或不同类型的子集上直接比较均分。

GEdit 官方同时提供 Full set 和 Intersection subset 口径。若只比较效果，可以预先选择其中一个官方子集，但所有模型必须使用同一批实例；Full set 与 Intersection subset 的结果应分开报告，不直接混比。

## 5. 中英文与 judge 版本

- 同一实例有英文和中文指令，应分别报告 EN/CN。
- `G_*` 与 `Q_*` 代表不同 judge 体系，原始分不能直接比较。
- 官方提示 GPT judge 对同图可能有约 0.1 的波动，需保存原始输出、固定模型版本，并视预算重复评分。

## 6. 为什么还需要背景保持指标？

GEdit 的 SC 是 MLLM 综合判断，适合开放编辑；但对“背景像素/纹理是否被重绘”不一定足够敏感。因此局部编辑建议再加：

- mask 外 LPIPS↓；
- mask 外 PSNR/SSIM↑；
- 身份保持指标（若涉及人物/主体）。

详见 [背景保持](10_MaskedBackgroundPreservation.md)。

## 7. 常见误用

- 只报 Overall，不报 SC/PQ；
- 把 GPT 与 Qwen judge 的分数混在一列；
- 把 Full set 与 Intersection subset 的均分直接比较；
- 用高 PQ 证明编辑成功；
- 只报英文，忽略中文指令差异。

## 8. 详细原始资料

主资料库：[GEdit-Bench 完整指标卡](../evaluation/06_editing_multimodal/02_GEdit-Bench/)

官方：[数据](https://huggingface.co/datasets/stepfun-ai/GEdit-Bench) · [评分代码](https://github.com/stepfun-ai/Step1X-Edit/tree/main/GEdit-Bench)
