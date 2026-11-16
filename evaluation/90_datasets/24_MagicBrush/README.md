# MagicBrush

## 数据卡

- **任务**：人工标注的真实图指令编辑，支持单轮、多轮、mask-provided 与 mask-free。
- **规模**：**5,313 个 edit sessions、10,388 个 edit turns**。
- **形式**：每轮 `<source image, instruction, target image>`；多轮时下一轮源图是上一轮目标图，每 session 最多 3 轮。
- **来源**：MS COCO 真实图，标注者在 DALL·E 2 编辑平台上人工给出指令、mask 并筛选目标图。
- **split**：Train/Dev/Test 同时按 sessions 与 turns 统计，不能只用“train 图像数”概括。

## 适合指标

L1/L2、CLIP-I、DINO、CLIP-T、人工偏好；mask-provided 时可在 mask 区域计算相应指标。开放编辑更适合增加 VIEScore/GEdit 式语义评价。

## 优点与局限

人工目标图与多轮过程比自动合成数据更真实；但目标图由 DALL·E 2 产生，带模型风格偏差，L1/L2 会惩罚其他合理答案。不同后续工作可能过滤 test set，报告实际使用 turn/session 列表。

## 来源

- Zhang et al., **MagicBrush: A Manually Annotated Dataset for Instruction-Guided Image Editing**, NeurIPS 2023：[论文](https://arxiv.org/abs/2306.10012)
- 项目页：[osu-nlp-group.github.io/MagicBrush](https://osu-nlp-group.github.io/MagicBrush/)
- 数据：[osunlp/MagicBrush](https://huggingface.co/datasets/osunlp/MagicBrush)
