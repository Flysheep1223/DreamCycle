# GenAI-Bench / GenAI-Rank

## 数据卡

- **任务**：复杂组合文生图/视频对齐与自动评分器验证；本卡聚焦图像。
- **prompt**：**1,600 条**专业设计师来源的挑战性文本。
- **技能标签**：5,000+ 经人工核验的 basic/advanced 组合技能标签。
- **人工评分**：论文共发布 **38,400 个 1–5 级图文/视频对齐评分**，含多模型、多标注者；图像与视频的一致性需分开看。
- **GenAI-Rank**：用于成对排序/偏好验证的数据，和点估计 MOS 评价不同。

## 适合指标

[VQAScore](../../01_alignment/03_VQAScore/) 原始推荐场景，以及 CLIPScore、TIFA、DSG、HPS/ImageReward 等的元评价。可算 SRCC、成对准确率、模型级排序相关。

## 优点与局限

真实设计需求、密集技能标签和人工评分使其不仅可生成 benchmark，也可检验“评分器是否可靠”。局限是公开模型代际和 prompt 分布会随时间漂移；1–5 人工绝对分与 side-by-side 偏好不能混算。

## 来源

- Li et al., **GenAI-Bench**：[论文](https://arxiv.org/abs/2406.13743)
- 官方评测代码与数据入口：[linzhiqiu/t2v_metrics](https://github.com/linzhiqiu/t2v_metrics)
- 数据查看器：[GenAI-Bench DataViewer](https://huggingface.co/spaces/BaiqiL/GenAI-Bench-DataViewer)
