# DPG-Bench（Dense Prompt Graph Benchmark）

## 一句话介绍

专门评估**长、稠密、多实体 prompt**的基准，将文本拆成带依赖关系的问题，用 mPLUG-large 看图回答，统计全局、实体、属性、关系等语义覆盖。

- **提出论文**：ELLA（Tencent）
- **prompt 数**：**1,065**
- **原始 VQA**：mPLUG-large
- **官方默认每 prompt 图数**：`PIC_NUM=4`
- **分数**：常见为百分制/比例，越高越好

## 数据与问题类型

DPG-Bench 的 prompt 比“一个对象+一种属性”更密集，包含多个实体、属性和关系。官方常见分项为：

- **Global**：整体场景或全局描述；
- **Entity**：要求的对象是否存在；
- **Attribute**：实体的颜色、材质、形状等属性；
- **Relation**：实体间空间或语义关系；
- **Other**：其余可验证语义。

数据构建参考了 COCO、PartiPrompts、DSG-1k、Object365 等来源，并借助 GPT-4 扩写短描述为稠密描述，再做人工检查。它关注“文本里写了的是否都画出”，不是只判断图片看起来像不像同一场景。

## 评分流程

1. 为每条稠密 prompt 生成 4 张图，并按官方目录/分辨率组织。
2. 使用预先构建的 Dense Prompt Graph 问题及依赖关系。
3. mPLUG-large 对图像逐问题回答。
4. 按图结构和依赖规则汇总正确回答；再按 Global/Entity/Attribute/Relation/Other 聚合。
5. 按官方脚本得到 overall 与分项。

官方运行脚本的核心参数为：

```bash
bash dpg_bench/dist_eval.sh <IMAGE_ROOT_PATH> <RESOLUTION>
# 内部默认 PIC_NUM=4，VQA model=mplug
```

## 优点

- 对长 prompt 的多条件覆盖比单句 CLIPScore 更有针对性。
- 问题与依赖可解释，能定位是漏实体、错属性还是错关系。
- 数据与脚本公开，已成为统一多模态生成模型常见的语义评测之一。
- 每 prompt 4 图的固定设置降低单 seed 偶然性。

## 局限

- mPLUG-large 是评分上限之一，视觉文字、细粒度空间与数量的误判会进入分数。
- 长 prompt 问题多，计算成本高；问题图的遗漏或错误会影响覆盖。
- 不评感知质量、美学、推理知识本身或人类偏好。
- 只报 overall 会掩盖关系与属性通常更难；不同论文若图数、分辨率或 VQA 不同，不应直接比较。

## 推荐报告

给 overall 外同时给五个分项、有效 prompt 数、每 prompt 图数、分辨率、judge 版本和代码 commit。对模型自带 prompt 改写的情况，保存改写文本；否则高分可能来自将稠密输入简化，而非真正遵循全部原始要求。

## 官方来源

- Hu et al., **ELLA: Equip Diffusion Models with LLM for Enhanced Semantic Alignment**：[论文](https://arxiv.org/abs/2403.05135)
- 官方代码与 `dpg_bench`：[TencentQQGYLab/ELLA](https://github.com/TencentQQGYLab/ELLA)
- 项目页：[ella-diffusion.github.io](https://ella-diffusion.github.io/)

> DPG-Bench 与 DPG（Denoising Policy Gradient 等）无关；它也与 DSG 不是同一数据集，虽然采用类似的依赖式 QG/A 思路。
