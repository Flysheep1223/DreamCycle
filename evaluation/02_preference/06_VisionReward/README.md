# VisionReward

## 一句话介绍

把人类视觉偏好拆成层次化检查清单，用 VLM 对每个细粒度问题回答 yes/no，再按学习/拟合的权重汇总为可解释偏好分；同时支持图像与视频。

- **图像模型**：VisionReward-Image，基于 CogVLM2-Llama3-Chat-19B
- **图像数据**：VisionRewardDB-Image，官方标为约 **48K × 60 个维度**
- **视频数据**：约 33K × 64 维；本资料库只聚焦图像部分
- **输出**：各问题判断及加权总分；也可比较两个候选

## 评分流程

1. 输入图像、prompt 和一条 checklist 问题，例如是否有结构异常、文本是否匹配、某类细节是否自然。
2. VLM 对每个问题输出 yes/no 判断。
3. 按官方 `weight.json` 对问题结果加权，形成各维度和总体分。
4. 保存每个问题的答案与权重，定位总分变化来自哪些维度。
5. 若做两图比较，固定相同 prompt 和问题集，比较总分或按官方 compare 接口。

可抽象写为：

`R(x,p) = b + Σ_q w_q * a_q(x,p)`

其中 `a_q` 是问题判断或实现中对应的数值，`w_q` 是官方权重；实际符号方向与截距以代码为准，不应自行假设所有 yes 都是好事。

## 优点

- **细粒度、可解释**：相比单一奖励 logit，可以知道哪个视觉属性导致低分。
- 将主观偏好拆成较易校验的二值问题，便于抽查评审器错误。
- 图像与视频采用统一思路，权重和问题公开。
- 可做多维一致偏好优化：仅当一个候选在各相关维度一致更好时使用偏好对，减少维度冲突。

## 局限

- 每图几十次 VQA，推理成本显著高于 CLIP 系奖励模型。
- 总误差来自每个问题的 VLM 误判；二值回答也会丢失不确定性。
- 权重反映训练标注人群和目标，不是普适用户效用；换业务需重新验证。
- 维度多不等于严格独立；同一伪影可能影响多个问题，导致重复计权。
- 19B 级模型部署门槛较高，模型和权重版本必须冻结。
- 用作优化奖励后仍需独立人工验证，防止对检查清单的博弈。

## 与 MPS 的差别

MPS 主要通过条件化 CLIP 表示输出不同偏好的标量分；VisionReward 显式运行大量可解释 QA 并加权。前者推理更轻，后者诊断更强但成本更高。两者都不能替代 Soft-TIFA 等客观条件覆盖检查。

## 官方来源与使用

- Xu et al., **VisionReward: Fine-Grained Multi-Dimensional Human Preference Learning for Image and Video Generation**：[论文](https://arxiv.org/abs/2412.21059)
- 官方代码：[THUDM/VisionReward](https://github.com/THUDM/VisionReward)
- 图像模型：[THUDM/VisionReward-Image](https://huggingface.co/THUDM/VisionReward-Image)
- 图像数据：[THUDM/VisionRewardDB-Image](https://huggingface.co/datasets/THUDM/VisionRewardDB-Image)

```bash
python inference-image.py --bf16 --score
# 输入 image_path + prompt，使用官方问题清单和 weight.json
```
