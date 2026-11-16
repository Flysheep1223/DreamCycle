# DreamBench++ 数据集

## 数据卡

- **任务**：人工作准的个性化/主体驱动生成。
- **规模**：**150 张参考图、1,350 条 prompt**，每图 9 条。
- **prompt 类型**：4 写实、3 非写实、2 复杂/想象性。
- **类别**：objects、living subjects、styles，含人物、动物、物体和非自然风格。
- **来源**：Unsplash、Rawpixel、Google Image Search 等，经模型/人工筛选与 prompt 校准；使用图像时另查许可。

## 适合指标

GPT-4o 的 **Concept Preservation（CP）与 Prompt Following（PF）**，各 0–4；另可比较 DINO-I、CLIP-I、CLIP-T、RefVNLI 与人工 0–4 标注。

## 优点与局限

比 DreamBench 更大且风格/主体更丰富，强调 CP–PF Pareto；但商业 judge 成本和快照影响复现，人物细节/风格保持仍带主观性。不能将 1,350 prompt 误写为“每主体 20 prompt”。

## 来源

- Peng et al., **DreamBench++**, ICLR 2025：[论文](https://arxiv.org/abs/2406.16855)
- 项目页：[dreambenchplus.github.io](https://dreambenchplus.github.io/)
- 官方代码与数据入口：[yuangpeng/dreambench_plus](https://github.com/yuangpeng/dreambench_plus)
