# 通用语义对齐：VQAScore

## 1. 这个维度测什么？

VQAScore 直接把整张图和整段 prompt 交给生成式视觉问答模型，询问：

> 这张图是否展示“{prompt}”？请回答 yes 或 no。

取回答 **Yes 的概率**作为连续对齐分。它特别适合：

- 在自己的中文/英文业务 prompt 集上快速大规模评分；
- 比较同 prompt 下不同模型的整体语义遵循；
- 作为 CLIPScore 之外更强的通用语义指标。

## 2. 公式与聚合

`VQAScore(x,t) = P("Yes" | x, question(t))`

通常位于 0–1，越高越好。对数据集取图像均值，或先对 prompt 多 seed 平均再对类别宏平均。

它不是“人类认为正确的概率”，而是**当前 VQA judge 的 Yes 概率**。不同 judge 的校准和分数尺度可能完全不同。

## 3. 数值例子

Prompt：

> 一只棕色的狗在草地上追赶一只黑色的狗。

假设同一固定 judge 对三个候选输出给出：

| 候选 | 图像内容 | Yes 概率 | 解释 |
|---|---|---:|---|
| A | 棕狗正在追黑狗，草地背景 | 0.91 | 主体、颜色、动作、场景均符合 |
| B | 棕狗和黑狗并排坐着，没有追逐 | 0.58 | 主体和颜色对，但关键动作没完成 |
| C | 草地上两只猫在追逐 | 0.04 | 动作和场景类似，但主体错误 |

如果有三条 prompt，某模型得分分别为 `0.91、0.72、0.44`，则简单图像均值为：

`(0.91+0.72+0.44)/3 = 0.69`

真实报告中还应给每条 prompt 的多 seed 均值和类别分项，而不是只报 0.69。

## 4. 为什么比 CLIPScore 更值得做主指标？

考虑候选 B：“两只狗并排坐着”。CLIP 可能仍因棕色、黑色、狗、草地等概念齐全而给较高分。VQAScore 使用生成式 VLM 对整句进行判断，通常更有机会识别“没有追逐”。

但它并非万无一失：judge 也可能只看主体而忽略动作，所以仍要配合 Soft-TIFA 和人工抽查。

## 5. 在私有 Seedream 评测集中的用法

给每条 prompt 保存：

```json
{
  "prompt_id": "zh_spatial_003",
  "prompt": "红色杯子在蓝盘子上，黄色杯子在绿盘子上",
  "seed": 0,
  "vqascore": 0.76,
  "judge": "exact-vlm-checkpoint",
  "question_template": "Does this figure show \"{}\"? Please answer yes or no."
}
```

推荐分别报告：

- 全部 prompt 的平均 VQAScore；
- 中文/英文；
- 属性绑定、数量、空间、动作、长 prompt；
- 每 prompt 4 seed 的均值和标准差；
- 与人工成对偏好的一致率。

## 6. VQAScore 与 Soft-TIFA 怎么分工？

| 场景 | 更合适的方法 |
|---|---|
| 自有 500 条业务 prompt，想快速评分 | VQAScore |
| 需要知道具体哪个原子错了 | Soft-TIFA / DPG |
| 需要衡量多条件联合满足 | Soft-TIFA GM |
| 需要批量通用语义回归测试 | VQAScore |
| 需要人工审查问题级失败 | Soft-TIFA / DPG |

两者可以组合，而不是互相替代。

## 7. 常见误用

- 把 `0.9` 解读为“90% 的人觉得正确”。
- CLIP-FlanT5 的分与 Qwen/GPT judge 的分直接比较。
- 不公开问题模板；改变问法可能改变结果。
- 长 prompt 只用一个 VQAScore，便声称知道所有细节都正确。
- 只报整段 VQAScore，不检查低分图像是否存在真实的漏对象或错关系。

## 8. 详细原始资料

主资料库：[VQAScore 完整指标卡](../evaluation/01_alignment/03_VQAScore/)

官方：[论文](https://arxiv.org/abs/2404.01291) · [代码](https://github.com/linzhiqiu/t2v_metrics)
