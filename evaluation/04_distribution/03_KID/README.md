# KID（Kernel Inception Distance）

## 一句话介绍

在 Inception 特征空间用多项式核的最大均值差异（MMD）比较真实与生成分布，不像 FID 那样假设高斯，并采用无偏估计以降低有限样本偏差。

- **输入**：两个图像集合
- **输出**：越低越好；同分布期望为 0，无偏有限样本估计可能出现小负值
- **经典特征**：Inception v3 pool3
- **常见核**：`k(x,y)=(xᵀy/d + 1)^3`，其中 `d` 为特征维度

## 公式

`KID = MMD_u²(P_r,P_g)`，使用上述多项式核：

`1/(m(m-1)) Σ_{i≠j} k(x_i,x_j) + 1/(n(n-1)) Σ_{i≠j} k(y_i,y_j) - 2/(mn) Σ_iΣ_j k(x_i,y_j)`

无偏形式排除同集合对角项 `k(x_i,x_i)`，因此不会像包含有偏对角项的估计那样随样本量产生同样系统性偏移。

## 评分流程

1. 用与对比实验一致的 Inception 权重与预处理提取特征。
2. 固定生成/参考样本数；从集合重复抽取固定大小子集，计算 KID。
3. 报告子集大小、重复次数、均值与标准差，以及核参数和实现。
4. 若用 clean-fid，固定 `mode`；若复现旧论文，检查是否同一预处理。

## 优点

- 不需要将特征分布近似为高斯。
- 无偏 MMD 估计适合较小样本量，并可用重复子采样给出波动。
- 与 FID 共用 Inception 特征管线，便于历史对比。

## 局限

- 仍继承 Inception 特征的 ImageNet 偏差，可能不符合生成图的人类感知。
- 多项式核、特征层与实现决定测量什么；KID 与 FID 数值不可换算。
- 不使用 prompt，不能证明文图对齐。
- 小负值是估计波动的可能结果，不代表“比同一分布更好”，不应强行截断为 0。
- 参考域不匹配、resize 和压缩问题与 FID 一样存在。

## 与 FID/CMMD 如何选择

- 复现旧 GAN/扩散论文：按原协议报 FID 与 KID。
- 小样本且希望无偏集合比较：KID 比小样本 FID 更合适。
- 现代开放域图像、希望更丰富的 CLIP 表示与非高斯 MMD：考虑 [CMMD](../04_CMMD/)，但需接受其 CLIP 特征与核带宽依赖。

## 官方来源与实现

- Bińkowski et al., **Demystifying MMD GANs**, ICLR 2018：[论文](https://arxiv.org/abs/1801.01401)
- 推荐实现：[GaParmar/clean-fid](https://github.com/GaParmar/clean-fid)

```python
from cleanfid import fid
score = fid.compute_kid("generated/", "reference/", mode="clean")
```
