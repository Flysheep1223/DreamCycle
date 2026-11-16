# 参考图与主体保持：DINO-I、CLIP-I、DreamBench++、MMIG-AMS

## 1. 这个维度为什么必须“双轴”评价？

给定一张参考图和新 prompt，理想输出需要同时满足：

1. **Subject/Concept Preservation**：仍然是参考图中的那个主体、风格或概念；
2. **Prompt Following**：新动作、新场景、新服装、新构图等要求被完成。

只看主体相似度，会奖励“复制参考图”；只看文本对齐，会奖励“生成了同类别但完全不同的对象”。

## 2. 快速自动指标

### DINO-I

`DINO-I = cos(E_DINO(参考图), E_DINO(生成图))`

越高表示在 DINO 特征中视觉/主体更相似。

### CLIP-I

`CLIP-I = cos(E_CLIP(参考图), E_CLIP(生成图))`

越高表示 CLIP 图像语义更相似。

### 文本遵循

使用 CLIP-T 或更推荐的 VQAScore/Soft-TIFA，检查目标 prompt 是否完成。

> DINO-I 与 CLIP-I 的分数不是同一尺度，不能互换；不同 backbone、主体裁剪和 pooling 也改变结果。

## 3. 数值例子：三种典型输出

参考图：一只左耳有黑色斑点、戴红色项圈的特定小狗。

目标 prompt：

> 让这只小狗穿着宇航服，站在月球表面，地球挂在背景中。

假设得到：

| 输出 | 内容 | DINO-I ↑ | CLIP-I ↑ | VQAScore ↑ |
|---|---|---:|---:|---:|
| A | 保留斑点和项圈特征，穿宇航服在月球 | 0.86 | 0.82 | 0.93 |
| B | 一只相似品种的普通狗，穿宇航服在月球 | 0.61 | 0.66 | 0.94 |
| C | 几乎复制参考图，没有宇航服和月球 | 0.98 | 0.97 | 0.12 |

解释：

- **A 最合理**：身份保持与新 prompt 都较好；
- **B 文本遵循高，但主体错了**：不能因为 VQAScore=0.94 就认为成功；
- **C 保持分最高，但没有完成任务**：不能因为 DINO-I=0.98 就认为最好。

以上数值仅用于解释指标方向。

## 4. 为什么整图相似度可能骗人？

如果参考图中主体只占 20%，背景占 80%，模型生成相同背景但换掉主体，整图 CLIP-I/DINO-I 仍可能很高。

改进方式：

- 用检测/分割框裁剪参考主体和输出主体后再算；
- 同时保留整图版，分析背景一致性；
- 多主体分别计算，不做一张整图 cosine 就结束；
- 人物身份需要时使用专门人脸模型与人工验证，但要注意许可和隐私。

## 5. DreamBench++：更接近人类的双维评分

DreamBench++ 使用 GPT-4o 按 0–4 分别评：

- **CP（Concept Preservation）**：形状、颜色、纹理、面部等概念是否保持；
- **PF（Prompt Following）**：新 prompt 是否相关、准确、完整。

前面的例子可对应为：

| 输出 | CP（虚构） | PF（虚构） | 判断 |
|---|---:|---:|---|
| A | 4 | 4 | 两者兼顾 |
| B | 2 | 4 | 新场景对，但身份不足 |
| C | 4 | 0 | 复制主体，没有遵循新场景 |

推荐看 **CP–PF Pareto**，而不是只把二者加成一个总分。

## 6. 多参考、多主体：MMIG-Bench / AMS

假设输入两张参考图：

- 参考 1：特定黑色背包；
- 参考 2：特定白色运动鞋。

Prompt：

> 将这两件商品放在同一张浅灰色产品海报中，背包在左，运动鞋在右，顶部写“URBAN DAILY”。

至少需要分别检查：

| 方面 | 检查问题 |
|---|---|
| 主体 1 | 是否是参考中的那个背包，而非普通黑包？ |
| 主体 2 | 是否保留参考鞋的轮廓、颜色和细节？ |
| 关系 | 背包是否在左，鞋是否在右？ |
| 文本 | URBAN DAILY 是否完全正确？ |
| 质量 | 两件商品是否自然融合、无伪影？ |

MMIG 的 **AMS** 将 prompt 拆成 aspect QA，用 Qwen2.5-VL-72B 回答并计算正确比例；低层另有 CLIP-I、DINOv2、CUTE 和伪影指标，高层另有偏好分。

多主体场景还应单独报告：

- 主体遗漏率；
- 主体串换率；
- 每个主体的保持分；
- 所有主体同时正确率。

## 7. 推荐数据与使用场景

| 场景 | 推荐 |
|---|---|
| 与旧 DreamBooth 论文比较 | DreamBench + DINO-I/CLIP-I/CLIP-T |
| 新一代单主体个性化 | DreamBench++ CP/PF + 人工抽检 |
| 多视角、多主体、多模态输入 | MMIG-Bench/AMS |
| 私有产品快速回归 | 主体裁剪 DINO-I + VQAScore + 人工双轴评价 |

## 8. 常见误用

- 把“同一品种”当成“同一个体”；
- 只报 DINO-I，不报 prompt 遵循；
- 多主体只报整图 CLIP-I；
- 参考图和输出图未对齐主体就盲目比较；
- 把 CLIP-I 与 DINO-I 的绝对值直接比较或平均。

## 9. 详细原始资料

主资料库：[CLIP-I](../evaluation/05_pairwise_reference/04_CLIP-I/) · [DINO-I](../evaluation/05_pairwise_reference/05_DINO-I/) · [DreamBench++](../evaluation/06_editing_multimodal/04_DreamBenchPP/) · [MMIG-Bench/AMS](../evaluation/06_editing_multimodal/06_MMIG-Bench/)
