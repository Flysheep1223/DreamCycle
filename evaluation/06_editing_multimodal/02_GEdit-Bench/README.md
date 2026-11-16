# GEdit-Bench

## 一句话介绍

来自真实用户编辑需求的 606 个实例、11 类任务和中英文指令，采用 VIEScore 式 MLLM 评审，分别输出语义一致性 SC、感知质量 PQ 与总体 O。

- **Full set**：606 个实例；不是 1,100
- **语言**：每个实例配英文与中文指令，可分 GEdit-Bench-EN/CN
- **评审器**：`G_*` 当前官方表为 GPT-4.1；`Q_*` 为 Qwen2.5-VL-72B
- **输出**：0–10，越高越好

## 11 类任务

官方统计代码中的类别为：

1. background_change
2. color_alter
3. material_alter
4. motion_change
5. ps_human
6. style_change
7. subject-add
8. subject-remove
9. subject-replace
10. text_change
11. tone_transfer

## 分数定义

- **SC / Semantic Consistency**：编辑结果是否遵循指令，包含应修改内容和相关保持要求。
- **PQ / Perceptual Quality**：图像自然度、真实感与伪影。
- **O**：每个样本先计算 `O_i = √(SC_i × PQ_i)`。

官方 `calculate_statistics.py` 先在每个任务内求平均，再对 **11 个任务等权宏平均**：

`G_O = (1/11) Σ_t (1/n_t) Σ_i √(SC_ti × PQ_ti)`

SC、PQ 也按同类宏平均。不是先对全 606 个样本直接算完再取一次总均值。

## Full set 与 Intersection

闭源模型可能因安全策略或调用失败不返回图像。官方论文因此同时给：

- **Intersection subset**：所有被比较方法都返回有效结果的共同子集；原论文 EN 为 434、CN 为 422。
- **Full set**：全部 606 个实例，但每个模型只对成功返回的样本求平均，失败/拒答样本不进入该模型均值。

**Full set 并不会在分数中直接惩罚拒答。** 产品比较必须另报无输出率、失败率，并考虑将失败纳入任务成功率；否则不同模型的有效样本并不相同。

## 复现细节与噪声

- 官方评审代码将源图和编辑图按长宽比缩放到约 512×512 面积后输入 VIEScore。
- GPT/Qwen 输出的原始分不同，G_SC 与 Q_SC 不可直接比较。
- 官方 EVAL 明确提示 GPT-4o 对相同输入也会波动，典型约 0.1；应固定快照、保存原始回复并重复抽样估计噪声。
- 官方发布部分中间结果，Qwen 路径更利于开放复现。

## 优点与局限

优点是真实指令、11 类分项、中英文、SC/PQ 解耦和开放 judge 路径。局限是 MLLM 误差、API 漂移、有效样本选择偏差，以及没有精确 mask 背景误差。对 OCR、数量等应加专项指标，对编辑过度应加掩码外 LPIPS/PSNR。

## 官方来源

- Liu et al., **Step1X-Edit: A Practical Framework for General Image Editing**：[论文](https://arxiv.org/abs/2504.17761)
- 官方代码与评分脚本：[stepfun-ai/Step1X-Edit/GEdit-Bench](https://github.com/stepfun-ai/Step1X-Edit/tree/main/GEdit-Bench)
- 数据：[stepfun-ai/GEdit-Bench](https://huggingface.co/datasets/stepfun-ai/GEdit-Bench)

```bash
python run_gedit_score.py --model_name your_model \
  --save_dir score_dir --backbone qwen25vl \
  --edited_images_dir your_edited_images_dir
python calculate_statistics.py --model_name your_model \
  --save_path score_dir --backbone qwen25vl --language en
```
