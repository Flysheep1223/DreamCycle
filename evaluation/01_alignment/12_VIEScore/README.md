# VIEScore（Visual Instruction-guided Explainable Score）

## 一句话介绍

让多模态大模型根据任务指令输出**语义一致性 SC、感知质量 PQ、总体分 O 和自然语言理由**，适用于文生图、编辑、主体驱动及其他条件图像生成。

- **分数**：SC、PQ、O 通常均为 0–10，越高越好
- **主要组成**：SC 看条件/指令与保持要求；PQ 单看输出图的视觉质量
- **总体分**：`O = sqrt(SC * PQ)`
- **关键优点**：可解释、任务通用，而不是把不同任务硬塞进一个 CLIP cosine

## 评分流程

1. 根据任务选择官方 prompt 模板，将输入条件（文本、源图、参考图等）与生成图交给 MLLM。
2. 语义部分拆成若干必要问题，例如“是否添加指定对象”“未指定区域是否保持”。SC 对子要求采用严格聚合，原方法用最低子分等方式防止某项完全失败被其他项补偿。
3. PQ 独立询问生成图的感知质量，关注真实感、伪影和视觉自然度，尽量避免 prompt 难度干扰。
4. 要求模型先给理由再给数值，保存完整原始回复。
5. 计算几何平均 `O=√(SC·PQ)`；SC 或 PQ 任一为 0，O 也为 0。

官方代码支持 T2I、文本引导编辑、多模态指令编辑、受控生成、主体驱动生成/编辑等任务类型，并支持 zero-shot/one-shot 及多种 MLLM backbone。

## 为什么用几何平均

编辑图如果完全遵循指令但充满伪影，不应获得高总分；如果很美但没有执行指令，也不应高总分。乘法/几何平均比简单相加更能表达“两者都不可缺”。它仍是人为设计的效用函数，不意味着每点差距具有相同心理意义。

## 优点

- 一个框架覆盖多种条件生成，尤其适合文本+图像输入。
- SC、PQ 分开，能区分“没听懂”和“画不好”。
- rationale 便于人工抽查与失败归因。
- 比 PSNR/SSIM 更适合没有唯一目标图、存在多种合理输出的任务。

## 局限

- 结果强依赖 MLLM、模板、图像输入顺序、分辨率、采样参数和 API 版本；不同 backbone 的 8 分不是同一尺度。
- judge 可能产生位置偏差、语言先验、对某种生成风格的偏好，rationale 合理也不保证视觉判断正确。
- 几何平均会传播 SC/PQ 的误差；很低的一项可能来自 judge 解析或提问歧义。
- 商业 MLLM 成本高且会更新，开放模型复现更稳定但能力可能不同。
- 不能替代可精确验证的数量、OCR、像素保持或掩码外指标；最好组合使用。

## 推荐实践

- 成对比较时随机交换左右并检测位置偏差；单图评分重复多次估计噪声。
- 固定官方任务模板，公开完整 prompt 与原始输出；解析失败单独计数。
- 同时报 SC、PQ、O，不只报 O；与人工成对偏好做相关性验证。
- 编辑任务另加掩码外 LPIPS/PSNR，文字任务另加 OCR 完全正确率。

## 官方来源

- Ku et al., **VIEScore: Towards Explainable Metrics for Conditional Image Synthesis Evaluation**, ACL 2024：[论文](https://aclanthology.org/2024.acl-long.663/)，[arXiv](https://arxiv.org/abs/2312.14867)
- 项目页：[tiger-ai-lab.github.io/VIEScore](https://tiger-ai-lab.github.io/VIEScore/)
- 官方代码：[TIGER-AI-Lab/VIEScore](https://github.com/TIGER-AI-Lab/VIEScore)

```python
from viescore import VIEScore
vie_score = VIEScore(backbone="gemini", task="t2i")
sc, pq, overall = vie_score.evaluate(pil_image, text_prompt)
```
