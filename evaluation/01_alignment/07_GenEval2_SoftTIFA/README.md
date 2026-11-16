# GenEval 2 与 Soft-TIFA

## 一句话介绍

GenEval 2 是包含 800 条不同组合复杂度 prompt 的新基准；Soft-TIFA 用 VQA 对每个视觉原子的**正确答案概率**打分，再分别以算术均值测原子能力、几何均值测整 prompt 联合满足。

> 它不是原版 GenEval 的检测器升级，也不应沿用原版 overall 公式。

## 数据结构

官方 `geneval2_data.jsonl` 每条包含：

- `prompt`：英文文本；
- `atom_count`：对象、属性、关系、计数等原子数量；
- `vqa_list`：每个原子的 VQA 问题及正确答案；
- `skills`：与每个 QA 对应的 object、attribute、position、count 等技能标签。

共 **800 条 prompt**。组合度可从少量原子到多原子，用于分析错误是否随原子数增加而累积。

## Soft-TIFA 定义

设一条 prompt 有 `n` 个原子问题，VQA 分配给正确答案的概率为 `p_i∈[0,1]`。

### Soft-TIFA AM（Arithmetic Mean）

`S_AM = (1/n) * Σ_i p_i`

再在 benchmark 上取平均。适合**原子级/技能级能力估计**：一个原子失败不会让其他原子的信息全部消失。

### Soft-TIFA GM（Geometric Mean）

`S_GM = (Π_i p_i)^(1/n)`

再在 benchmark 上取平均。适合**prompt 级联合满足估计**：某个必要条件接近 0 会显著降低整体分，表达“所有条件都要成立”。采用 1/n 次方可减少仅因原子数不同造成的数值尺度变化，但多原子联合满足仍通常更困难。

## 评分流程

1. 为 800 条 prompt 生成图像，建立 prompt → 图像路径映射。
2. 固定 VQA judge，对每个 `vqa_list` 问题计算正确答案概率，而非只保留离散回答。
3. 保存每原子概率与技能标签。
4. AM 做原子/技能分析，GM 做 prompt/atomicity 分析。
5. 报告 VQA 精确模型、transformers 版本、输出概率提取方式、每 prompt 图数与聚合方式。

官方论文实验采用开放 VQA 模型；官方代码默认环境列出 `transformers==4.57.0`。论文中 Qwen3-VL-8B 配置被用于验证 Soft-TIFA，但任何替换 judge 的实验都应视为新配置并重新做人机一致性校验。

## 相比原版 GenEval 的改进

- 视觉概念覆盖更广，组合度更高，并带原子数与技能标注。
- 从检测器离散判断转为 VQA 概率，可保留“不确定”信息。
- 同时提供 AM 与 GM，明确区分“平均会多少原子”和“整条 prompt 联合满足多少”。
- 针对 benchmark drift：不能假设在旧模型上与人类一致的自动指标，对新一代模型仍保持同样误差。

## 局限

- VQA 的校准误差会进入 `p_i`，GM 对接近 0 的误判尤其敏感。
- 问题覆盖决定语义覆盖；标注 QA 若遗漏隐含条件，Soft-TIFA 也不会自动发现。
- AM 与 GM 回答不同问题，不应把二者平均成第三个“总分”。
- 仍主要评语义组合，不直接测审美、偏好、真实性或文字渲染。
- 数据许可以官方仓库为准；截至整理日官方标为 CC BY-NC 4.0，商业使用前需检查。

## 官方来源与运行

- Kamath et al., **GenEval 2: Addressing Benchmark Drift in Text-to-Image Evaluation**：[论文](https://arxiv.org/abs/2512.16853)
- 官方代码与数据：[facebookresearch/GenEval2](https://github.com/facebookresearch/GenEval2)

```bash
python evaluation.py \
  --benchmark_data geneval2_data.jsonl \
  --image_filepath_data your_image_paths.json \
  --method soft_tifa_gm \
  --output_file score_lists.json
python soft_tifa_analysis.py \
  --benchmark_data geneval2_data.jsonl \
  --score_data score_lists.json
```
