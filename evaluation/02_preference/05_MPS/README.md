# MPS（Multi-dimensional Preference Score）

## 一句话介绍

通过“偏好条件”控制同一 CLIP 系评分模型，分别学习整体、美学、语义对齐和细节质量偏好，试图回答人不只用一个标准选图的问题。

- **四个维度**：Overall、Aesthetics、Alignment、Detail
- **数据**：MHP，918,315 条人类偏好标注、607,541 张图
- **模型形式**：带 preference condition module 的 CLIP 表示与 logit-scale 相似度
- **发布限制**：截至整理日，官方 README 明确仅发布 **Overall checkpoint**，完整多维模型仍待发布

## 评分原理

输入 prompt、图像以及表示评价维度的 condition 文本。模型在条件控制下产生图文表示并计算：

`s_d(x,y) = exp(logit_scale) * <E_txt(x,condition_d), E_img(y,condition_d)>`

其中 `d` 可以是 overall、aesthetic、alignment 或 detail。对同 prompt 两张图，将各自分数堆叠后 softmax，得到该维度下的相对偏好概率。

官方 overall 示例使用一串覆盖光照、色彩、清晰度、风格、构图、人体、结构、纹理、数量、属性、位置、文字等的 condition 文本。**condition 是模型输入的一部分**，改动它可能改变分数。

## 四个维度含义

- **Overall**：综合所有偏好的选择，适合与 HPS/PickScore 等比较。
- **Aesthetics**：构图、色彩、光照、艺术感等。
- **Alignment**：prompt 中的对象、数量、属性、位置等是否实现。
- **Detail**：局部结构、纹理、人体细节和视觉缺陷等。

这些维度仍可能有相关性，不应把四个分当作严格独立或互不重叠的测量。

## 优点

- 将单一人类偏好拆解为可选择的评价条件，更符合多目标产品需求。
- MHP 数据规模较大，并覆盖多维标注。
- 同一架构下可研究整体偏好与各子维度的关系，也可做多目标偏好优化。

## 局限与复现风险

- **开源权重限制是实际使用关键**：公开仓库提供的是 overall 模型，不能凭论文表格声称已复现四个维度。
- condition 文本、CLIP backbone 和 checkpoint 必须完全一致；任意改写 condition 会形成新评分协议。
- 与所有奖励模型一样，有训练数据域偏差、绝对分跨 prompt 不可校准和 reward hacking 风险。
- 多维偏好标注不必然等价于各维度的客观真值，需要看标注协议与人际一致性。

## 官方来源

- Zhang et al., **Learning Multi-dimensional Human Preference for Text-to-Image Generation**, CVPR 2024：[论文](https://openaccess.thecvf.com/content/CVPR2024/papers/Zhang_Learning_Multi-Dimensional_Human_Preference_for_Text-to-Image_Generation_CVPR_2024_paper.pdf)
- 官方代码与 Overall checkpoint 入口：[Kwai-Kolors/MPS](https://github.com/Kwai-Kolors/MPS)
- 项目页：[wangbohan97.github.io/MPS](https://wangbohan97.github.io/MPS/)

> 写报告时建议明确 `MPS-overall (public checkpoint)`；若使用作者未公开的多维结果，应注明来自论文而非本地复现。
