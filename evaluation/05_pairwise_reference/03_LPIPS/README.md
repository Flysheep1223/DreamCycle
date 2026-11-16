# LPIPS（Learned Perceptual Image Patch Similarity）

## 一句话介绍

用深度网络多层特征及学习到的通道权重比较配对图像，通常比 PSNR/SSIM 更接近人类对 perceptual similarity 的判断；输出是距离，越低越相似。

- **输入**：输出图与参考图，通常同尺寸
- **输出**：非负距离，0 表示相同；越低越好
- **常见 backbone**：AlexNet、VGG、SqueezeNet
- **常见用途**：恢复、图像翻译、编辑保持、同 prompt 组内多样性（此时距离高表示差异大）

## 公式

对网络第 `l` 层特征 `φ_l`，先在通道维归一化，学习权重 `w_l`，再计算空间平均：

`d(x,y) = Σ_l (1/(H_lW_l)) Σ_hw ||w_l ⊙ (φ_l(x)_hw - φ_l(y)_hw)||²`

不同 backbone 和 linear/calibration 配置会产生不同数值，不能跨配置比较。

## 三种常见用途

1. **重建质量**：输出越接近目标图，LPIPS 越低。
2. **编辑未编辑区保持**：应只在背景/掩码外定义；全图低分可能意味着没编辑。
3. **组内多样性**：同 prompt K 张图的两两 LPIPS 均值，越高越多样；但必须排除错误输出，否则“坏得各不相同”也高分。

## 优点

- 深度特征对纹理、结构和局部感知差异通常比像素误差更合理。
- 可微，能用于训练损失，也能用于独立评价。
- 推理相对轻量，有成熟 PyTorch 实现和人类相似度标定基础。

## 局限

- 不是文图对齐指标，不读取 prompt；不同但合理的输出相对参考仍会有距离。
- 配对图像若未对齐，LPIPS 也可能惩罚合理构图变化。
- 训练为相似度判断，不保证专门识别手部、拼写或所有生成伪影。
- **mask 版实现不唯一**：卷积感受野会跨越 mask 边界，简单将特征乘 mask 与先裁背景并不等价；应遵循 PIE-Bench 等具体实现。
- 用于训练优化后，作为唯一独立评测可能产生循环。

## 推荐报告

`LPIPS / backbone / version / input range & resize / full-image or masked / mean pairwise or paired-reference`。多样性实验同时报告语义成功率与每 prompt K。

## 官方来源与实现

- Zhang et al., **The Unreasonable Effectiveness of Deep Features as a Perceptual Metric**, CVPR 2018：[论文](https://arxiv.org/abs/1801.03924)
- 官方代码：[richzhang/PerceptualSimilarity](https://github.com/richzhang/PerceptualSimilarity)
- 另一常用实现：[photosynthesis-team/piq](https://github.com/photosynthesis-team/piq)

```python
import lpips
loss_fn = lpips.LPIPS(net="alex")
d = loss_fn(img0, img1)  # 按库要求将输入归一化到[-1,1]
```
