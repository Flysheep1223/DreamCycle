# CMMD（CLIP Maximum Mean Discrepancy）

## 一句话介绍

以 CLIP 图像 embedding 替代 Inception，并用高斯 RBF 核的 MMD 比较真实和生成分布；不做高斯假设，官方强调无偏、样本效率和更好的人类判断一致性。

- **输入**：参考图集 + 生成图集
- **官方特征**：CLIP **ViT-L/14@336px**
- **输出**：距离，越低越好；不能解释为百分比
- **官方示例**：COCO 2014 val，两目录各最多 30,000 张图

## 公式

对特征样本 `x∼P`、`y∼Q`，RBF 核：

`k(x,y)=exp(-||x-y||²/(2σ²))`

`CMMD` 基于：

`MMD²(P,Q)=E[k(x,x′)] + E[k(y,y′)] - 2E[k(x,y)]`

实现采用相应的无偏样本估计。核带宽 `σ`、特征归一化、具体估计和数值缩放必须随官方实现固定。

## 与 FID 的差别

| 方面 | FID | CMMD |
|---|---|---|
| 特征 | Inception v3 | CLIP ViT-L/14@336px |
| 分布假设 | 两个高斯 | 非参数 MMD，无高斯假设 |
| 距离 | Fréchet | RBF-kernel MMD |
| 有限样本 | 偏差较明显 | 官方强调无偏与样本效率 |
| 数值 | 不可互换 | 不可互换 |

虽然使用 CLIP，CMMD **仍然不读取 prompt**，不是 CLIPScore，也不测逐条文图对齐。

## 优点

- 更丰富的视觉表示，避免过度依赖 ImageNet 分类特征。
- 无需高斯近似；MMD 能捕捉超出均值/协方差的分布差异。
- 在较少样本下更实用，官方论文报告与人类判断更一致的结果。
- 两个输入目录可交换，概念清晰。

## 局限

- CLIP 也可能忽略细小纹理失真、局部结构错误和文字错误；特征更现代不等于全面。
- 结果受核带宽、特征 checkpoint、预处理和 max_count 影响。
- COCO 2014 val 分辨率偏低；官方 README 明确提醒它不适合检验 1024×1024 等高分辨率生成的全部质量。
- 参考域不匹配时仍可能奖励“像 COCO”而非任务成功。
- 不评估单条文本语义，也不能取代 Precision/Recall 的保真—覆盖分解。

## 推荐实践

- 使用官方代码与同一 CLIP 权重；两目录使用匹配 prompt 的真实/生成图。
- 固定 N，并做多次不重叠子采样报告均值/区间。
- 若研究高分辨率细节，选择匹配分辨率与内容域的参考集，同时用配对/人工指标补充。
- 与 Soft-TIFA/VQAScore 和人工偏好一起报告，不以 CMMD 单独宣布综合领先。

## 官方来源与运行

- Jayasumana et al., **Rethinking FID: Towards a Better Evaluation Metric for Image Generation**, CVPR 2024：[论文](https://arxiv.org/abs/2401.09603)
- 官方实现：[google-research/cmmd](https://github.com/google-research/google-research/tree/master/cmmd)

```bash
python -m cmmd.main /path/to/reference/images /path/to/eval/images \
  --batch_size=32 --max_count=30000
```
