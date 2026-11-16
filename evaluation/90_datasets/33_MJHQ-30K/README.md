# MJHQ-30K

## 数据卡

- **任务**：高美学质量生成图参考分布与 FID 评价。
- **规模**：**30,000 张图，10 个常见类别，每类 3,000 张**。
- **来源**：从 Midjourney 5.2 生成结果中筛选，结合 aesthetic 与 CLIP score 控制质量和对齐。
- **原始协议**：Playground v2.5 使用 1024×1024 图像计算 overall 与各类别 FID。

## 适合指标

[FID](../../04_distribution/02_FID/) 为主，也可在固定预处理下计算 CMMD/KID 或类别内分布指标；生成 prompt 应与参考类别/文本协议对应。

## 关键局限

参考图本身也是生成图且经美学筛选，所以低 FID 表示“更接近这套 MJ 高审美分布”，不等于真实照片分布、文图对齐或普遍人类偏好。筛选过程还可能降低多样性；若模型训练已使用 MJHQ-30K，不能再作为独立测试。

## 来源

- Li et al., **Playground v2.5: Three Insights towards Enhancing Aesthetic Quality in Text-to-Image Generation**：[论文](https://arxiv.org/abs/2402.17245)
- 官方数据：[playgroundai/MJHQ-30K](https://huggingface.co/datasets/playgroundai/MJHQ-30K)
