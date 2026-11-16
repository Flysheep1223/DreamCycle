# ImgEdit-Bench

## 数据卡

- **任务**：统一图像编辑，含基础、困难单轮与多轮。
- **Basic-Edit**：**734 个 test cases**，9 类：add、remove、alter、replace、style transfer、background change、motion change、hybrid edit、cut-out。
- **UGE Suite**：**47 张复杂图**，测 understanding-grounding-editing，含遮挡、多实例、伪装对象等。
- **Multi-Turn Suite**：content memory、content understanding、version backtracking 各 10 个案例，每例 3 轮交互。

## 评分

GPT-4o 以 1–5 评 instruction adherence、editing quality、detail preservation；后两项 capped at adherence，防止完全没听懂仍靠美观高分。多轮由人工 yes/no；另有 FakeShield fake score 和 ImgEdit-Judge 开放评审器。

## 优点与局限

覆盖复杂定位、多轮记忆和回滚，且给三维解耦；但 judge 训练/评分来源需区分，FakeShield 也是模型预测而非真值。ImgEdit 训练集与 Bench 必须严格隔离。

## 来源

- Ye et al., **ImgEdit: A Unified Image Editing Dataset and Benchmark**, NeurIPS 2025：[论文](https://arxiv.org/abs/2505.20275)
- 官方代码与数据：[PKU-YuanGroup/ImgEdit](https://github.com/PKU-YuanGroup/ImgEdit)
