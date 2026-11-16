# Control Consistency（可控生成条件一致性）

## 一句话介绍

对 ControlNet/T2I-Adapter 等条件生成，不应用一个通用 CLIP 分代替所有控制精度；应从输出图重新预测分割、姿态、边缘、深度或对象，再与输入条件计算任务对应误差。

- **输入**：控制条件 `c`、生成图 `x`、可选 prompt
- **输出**：依条件类型而定，方向不同，不能不分归一化就平均
- **核心原则**：尽量使用与生成模型独立的预测器，并报告其误差和置信度

## 各条件的标准指标

### 1. 语义/实例分割：mIoU

对输出图运行分割模型，与输入 segmentation condition 比较：

`IoU_c = |Pred_c ∩ Cond_c| / |Pred_c ∪ Cond_c|`

`mIoU = (1/C) Σ_c IoU_c`

越高越好。需说明忽略类、分辨率、类别映射和空类处理；也可补 pixel accuracy，但类别不均衡时 mIoU 更有意义。

### 2. 对象/布局：IoU、mAP

将条件中的对象框/类别与输出检测结果匹配。单框可报 IoU；多对象和开放检测通常报不同 IoU 阈值下的 AP/mAP。若条件只有布局而无类别真值，应分别评估类别正确、框位置与数量，不能只算检测器找到了“某个对象”。

### 3. 人体姿态：OKS / AP

对关键点 `i`：

`OKS = Σ_i exp(-d_i²/(2s²k_i²)) δ(v_i>0) / Σ_i δ(v_i>0)`

`d_i` 为预测与条件关键点距离，`s` 为人体尺度，`k_i` 为关键点常数。常报 OKS=0.50:0.95 的 AP 或平均 OKS。检测不到关键点的惩罚和不可见点规则必须公开。

### 4. 边缘/线稿：Boundary F-score

在输出图提取边缘，与条件边缘在距离容差内做 precision/recall：

`F = 2PR/(P+R)`

容差以像素或图像对角线比例表示。边缘检测器、阈值和 thinning/dilation 会显著影响结果；可同时报 ODS/OIS（若适用）。

### 5. 深度：AbsRel、RMSE、δ

- `AbsRel = mean(|d̂-d|/d)`，越低越好；
- `RMSE = sqrt(mean((d̂-d)²))`，越低越好；
- `δ_t = mean(max(d̂/d,d/d̂)<t)`，越高越好，常见 `t=1.25`。

相对深度需先做规定的 scale/shift alignment；绝对深度则不能任意归一化。无效像素与天空/远景处理应固定。

### 6. 法向、涂鸦、色彩等

法线图常报 mean/median angular error 与指定角度内比例；涂鸦/线稿可用边缘 F1 或 SSIM；色彩条件需在规定色彩空间比较。每个都应写清几何和数值定义。

## 推荐评测协议

1. 固定条件到输出图像的 resize、 cropping 与坐标变换。
2. 用独立、公开检测器从输出恢复条件，记录 checkpoint 和置信度阈值。
3. 同一条件生成多 seed，报均值和至少一次满足率。
4. 报**条件一致性 + 文本对齐 + 感知质量**三轴：满足姿态但画错对象、图像漂亮但偏离布局，都不是完全成功。
5. 对空条件、遮挡、多人、多对象和低置信预测保留失败样本，不静默删除。

## 主要局限

控制条件的“真值”由另一个模型预测，评测上限受检测器限制；域外艺术图和遮挡会产生假阴性。不同条件的指标不可直接平均，应在每类内部排名或先设业务门槛。

## 参考来源

- Zhang et al., **Adding Conditional Control to Text-to-Image Diffusion Models (ControlNet)**：[论文](https://arxiv.org/abs/2302.05543)
- COCO 检测/姿态评价：[COCO evaluation](https://cocodataset.org/#detection-eval)
- mIoU 背景：Long et al., **Fully Convolutional Networks for Semantic Segmentation**：[论文](https://arxiv.org/abs/1411.4038)
- 边界评价：Martin et al., **Learning to Detect Natural Image Boundaries Using Local Brightness, Color, and Texture Cues**：[DOI](https://doi.org/10.1109/TPAMI.2004.1273918)
