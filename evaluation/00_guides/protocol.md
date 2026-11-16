# 可复现评测协议与报告模板

## 1. 冻结生成侧配置

每次运行生成一份不可变 manifest：

```json
{
  "model_id": "组织/模型与精确revision",
  "model_version_or_commit": "...",
  "task": "t2i | editing | subject_driven | control",
  "prompt_set": "名称、版本、文件sha256",
  "num_images_per_prompt": 4,
  "seeds": [0, 1, 2, 3],
  "sampler": "...",
  "steps": 28,
  "guidance_scale": 3.5,
  "width": 1024,
  "height": 1024,
  "negative_prompt": "...",
  "prompt_rewrite": false,
  "safety_filter": "...",
  "postprocessing": "无/超分/refiner/watermark",
  "hardware": "...",
  "run_date": "YYYY-MM-DD"
}
```

同一比较中保持推理预算一致。若比较 API 模型无法获得 seed、采样器或精确版本，必须明确写“黑盒服务、评测日期”，不要假装完全受控。

## 2. Prompt 集与数据隔离

- 固定原始 prompt；如果模型自带改写，分别评测“原始输入”和“系统实际输入”，保存改写结果。
- 训练集、奖励模型训练集、prompt 开发集与最终测试集分开。测试集调参后应另留 held-out 集。
- 对公开基准的图像、prompt、QA 和人工标签做泄漏检查；不要用测试集人工标注训练评审器。
- 多语言不是简单翻译：保留文化实体、书写系统、标点和分词差异，并记录翻译方式。

## 3. 采样与估计目标

先声明要测哪一种能力：

- **单次期望质量**：每条 prompt 用预先固定的 K 个 seed，全部计分并平均。
- **best-of-K**：每条 prompt 取最高分；同时报告 K 与选择器，不能和单样本结果比较。
- **至少一次成功**：`1/K * Σ_i 1[Σ_k correct_ik > 0]`，反映交互产品中允许重抽的体验。
- **稳定性**：同一 prompt 多 seed 的成功率方差、组内多样性，不只报告均值。

建议同时给逐样本结果与宏平均。对 FID/CMMD 等集合指标，固定 N 并用多次不重叠抽样估计波动。

## 4. VLM/MLLM judge 规范

1. 固定模型提供方、模型 ID、快照日期、temperature、top-p、最大 token、输入分辨率与完整 prompt 模板。
2. 优先结构化 JSON 输出，并保留 rationale、原始回复、重试和解析失败；不能悄悄把解析失败当 0 或删除。
3. 成对比较随机交换左右顺序，分别运行 A-B 与 B-A 可检测位置偏差；同分时允许 tie。
4. 点评分至少重复 2–3 次估计 judge 噪声。GEdit-Bench 官方明确提示 GPT-4o 对同一输入通常也可能有约 0.1 的波动。
5. 不让 judge 看到模型名、来源、排名或无关元数据；对图像做一致的格式转换。
6. 定期用人工子集校验；新模型发布或 judge 更新后重新校验，旧分与新分不直接拼接。
7. 使用商业 API 时考虑数据隐私、费用、服务变更和可复现性；公开结果优先提供开放 VLM 复现路径。

## 5. 统计报告

### 均值与区间

设 prompt 级分数为 `s_i`，模型均值为 `s̄`。推荐以 **prompt 为重采样单位**做 bootstrap，而不是把所有问题当独立样本；同 prompt 的多图、多问题应整块重采样。报告 95% 百分位或 BCa 区间和重采样次数（例如 10,000）。

### 两模型配对差

对同一 prompt、尽可能相同 seed 的样本计算 `d_i=s_Ai-s_Bi`，对 prompt 做配对 bootstrap，报告 `mean(d)` 及区间。区间跨 0 时避免写“显著提升”。

### 成对人工比较

报告 A 胜、B 胜、平局及有效票数：

`win_rate(A) = (wins_A + 0.5 * ties) / valid_comparisons`

同时给“不计平局胜率”与“平局计半胜率”，避免口径歧义。区间可按每个独立比较做二项/bootstrap 估计；同一标注者、同一 prompt 的重复票应聚类处理。

### 多模型与多重比较

Elo/BT 排名之外保留原始两两矩阵、连通性、tie 规则和区间。大量分项检验时控制多重比较；不根据测试集结果反复调整 prompt 或权重。

## 6. 结果目录建议

```text
run_id/
├── manifest.json
├── prompts.jsonl
├── images/
├── generations.jsonl        # 每张图的seed、路径、耗时、错误
├── raw_judge_outputs/       # 未修改的原始评审回复
├── sample_scores.jsonl      # 原子、问题、图像、prompt各级分
├── aggregate.json           # 均值、宏平均、区间、样本数
└── failures.md              # 典型失败及漏评/解析失败
```

## 7. 最小结果表模板

| 字段 | 必填内容 |
|---|---|
| 模型 | 名称、精确版本、开放/闭源、评测日期 |
| 数据 | benchmark 版本、prompt 数、语言、参考 split |
| 采样 | 分辨率、steps、guidance、每 prompt 图数、seed、改写/后处理 |
| 指标 | 实现仓库 commit、checkpoint、judge、输入尺寸 |
| 聚合 | 图像/问题/prompt 层级、算术/几何/宏平均、best-of-K 与否 |
| 结果 | 总分、分项、有效样本数、失败数、95% 区间 |
| 可审计性 | 逐样本分、原始 judge 回复、图像与配置是否公开 |

## 8. 发布前检查

- [ ] 没有跨版本比较 CLIP/HPS/VLM 原始分。
- [ ] 没有把单图指标和集合指标混算。
- [ ] 没有只用最好 seed 或最好一张图代表平均能力。
- [ ] 编辑结果同时有“编辑成功”和“无关区域保持”。
- [ ] 偏好指标若参与训练，另有独立指标和人工校验。
- [ ] OCR 有严格完全正确率，且公开文本归一化规则。
- [ ] 所有榜单数字均可由逐样本结果重新聚合。
