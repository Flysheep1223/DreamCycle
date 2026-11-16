# CLIP-I（Image–Image CLIP Similarity）

## 一句话介绍

分别用 CLIP 图像编码器编码参考图和生成图，计算图像 embedding 余弦相似度，衡量整体视觉语义/主体保持；与文本—图像的 CLIPScore/CLIP-T 不同。

- **输入**：参考图与生成图，不需要文本
- **输出**：cosine，越高越相似；有时会乘 100
- **常见用途**：DreamBooth/个性化生成的 CLIP-I、编辑内容保持、参考图一致性
- **不能单独使用**：原图不变或复制参考背景也可能得高分

## 公式

`CLIP-I(x_ref,x_gen) = cos(E_img(x_ref),E_img(x_gen))`

使用同一 CLIP 图像编码器和相同预处理。若是多张参考图，需说明逐参考计算后取均值/max，还是先融合参考特征；两种协议不同。

## 主体驱动评测中的标准搭档

- CLIP-I：生成图—参考图，测视觉/主体保持。
- DINO-I：另一自监督表示下的主体保持。
- CLIP-T / VQAScore：生成图—目标 prompt，测文本遵循。

必须同时报告“保持”和“遵循”，否则容易偏向直接复制参考图而不执行新场景/动作。

## 优点

- 无需像素对齐，对姿态、视角和局部变化比 PSNR/SSIM 更宽容。
- 推理快，与 CLIP-T 可共用编码器。
- 对整体物体类别、场景、风格和部分身份特征有响应。

## 局限

- 整图 embedding 同时包含背景、构图和风格；主体错但背景相同也可能高分。
- 对细粒度身份、品种、Logo、具体面部特征和空间关系不一定可靠。
- CLIP backbone、裁剪和是否先检测主体显著改变结果。
- 高 CLIP-I 可能奖励最小改动，不能证明编辑或新 prompt 被实现。
- 与其他 CLIP 权重的绝对分不可直接比较，也不表示人类身份一致率。

## 改进实践

- 用检测/分割框裁剪参考与生成主体后再算，并保留整图版作背景一致性。
- 多主体分别匹配，防止只保留最显眼主体；记录主体对应关系。
- 与 DINO-I、VQAScore、人工身份比较联合；人脸身份可用专门人脸识别模型，但应单独说明误差和隐私许可。

## 来源

- Radford et al., **Learning Transferable Visual Models From Natural Language Supervision (CLIP)**：[论文](https://arxiv.org/abs/2103.00020)
- Ruiz et al., **DreamBooth: Fine Tuning Text-to-Image Diffusion Models for Subject-Driven Generation**（采用 DINO、CLIP-I、CLIP-T 评价体系）：[论文](https://arxiv.org/abs/2208.12242)
- 官方 CLIP：[openai/CLIP](https://github.com/openai/CLIP)
