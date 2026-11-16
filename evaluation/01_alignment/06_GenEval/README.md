# GenEval（原版，Object-Focused Evaluation）

## 一句话介绍

用目标检测/分割等判别模型检查生成图中对象是否存在、数量、颜色、位置和属性绑定是否正确，将文图对齐变成可审计的实例级规则判断。

- **输入**：553 条结构化 prompt 及每条 prompt 的生成图
- **原始生成协议**：每 prompt 4 张图
- **检测器**：官方使用 Mask2Former，并结合 CLIP 检查颜色等属性
- **输出**：0–1；主 overall 为六个任务分的等权平均，越高越好

## 六类任务与官方 prompt 数

| 任务 | 检查内容 | prompt 数 |
|---|---|---:|
| Single object | 单个指定对象是否存在 | 80 |
| Two object | 两个对象是否共同出现 | 99 |
| Counting | 指定对象数量 | 80 |
| Colors | 对象及颜色 | 94 |
| Position | 两对象的相对位置 | 100 |
| Color attribution | 颜色是否绑定到正确对象 | 100 |
| **总计** |  | **553** |

## 评分逻辑

以“两个红色球和一个蓝色立方体”为例：检测器先找球和立方体及数量，再验证颜色；位置任务根据检测区域判断 left/right/above/below 等关系；颜色归属任务要求每个对象绑定自己的颜色，不能只靠整图颜色统计。

官方 `summary_scores.py` 的主分数为：

`task_score_t = 该任务全部生成图的 correct 均值`

`GenEval Overall = (1/6) * Σ_t task_score_t`

官方还打印 **% correct prompts**：同一 prompt 的多张图中任意一张正确即算该 prompt 成功。这个“至少一次成功”与主 overall 不是同一估计目标，不能替换或混报。

## 优点

- 判断链条可检查：检测到什么、为何失败都能输出，优于黑盒单一 cosine。
- 对对象共现、计数、位置、颜色绑定等可组合能力尤其有针对性。
- 固定模板和检测规则减少自由文本 judge 的语言波动。
- 官方结果文件保留每图 `correct` 与 `reason`，便于逐样本审计。

## 局限

- 对象类别与检测器训练分布受限，开放世界实体、非写实风格和遮挡会降低评测可靠性。
- 原版属性主要集中于颜色，空间关系模板有限；不是通用语义或推理基准。
- 检测器/分割器的错误会被计为生成错误；需人工抽样估计 judge 假阳性/假阴性。
- 新模型在旧任务上提高后，自动指标可能与人工判断发生漂移。GenEval 2 论文报告原版在当代模型上的这类问题，因此新旧榜单不能仅按“overall 更高”解释。
- 不测感知质量、美学、视觉文字和整体人类偏好。

## 使用建议

- 复现原版时锁定官方仓库 commit、mmdetection 版本、检测权重和 4 图/prompt 协议。
- 同时保留每图结果，分别报告图像级主分、六任务分项和（如需要）prompt 至少一次成功率。
- 不要把 GenEval 原版与 [GenEval 2](../07_GenEval2_SoftTIFA/) 的 Soft-TIFA 分数直接连线比较；若需趋势，同批图像同时跑两版并标注 judge 差异。

## 官方来源

- Ghosh et al., **GenEval: An Object-Focused Framework for Evaluating Text-to-Image Alignment**：[论文](https://arxiv.org/abs/2310.11513)
- 官方代码、prompt 与汇总脚本：[djghosh13/geneval](https://github.com/djghosh13/geneval)

```bash
python evaluation/evaluate_images.py <IMAGE_FOLDER> \
  --outfile <RESULTS_FOLDER>/results.jsonl \
  --model-path <OBJECT_DETECTOR_FOLDER>
python evaluation/summary_scores.py <RESULTS_FOLDER>/results.jsonl
```
