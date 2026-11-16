r"""# examples 模块

`run_showcase.py` 会真实调用方舟，依次运行：

1. 两个超复杂原创二次元文生图；
2. 一张单参考角色新场景、一张双参考角色组合；
3. 两个限定条件的图像编辑任务。

```bash
uv run python -m EVA.examples.run_showcase
```

后四类复用前两张生成图，因此能完整覆盖多标签路由、多参考输入、OCR 和编辑/保持评分。每个案例有独立运行目录，父目录 `showcase-*/summary.json` 汇总成功与失败，单个案例失败不会取消其他独立案例。

这些样例用于验证系统能运行和定位失败，不构成 Seedream 的统计性质量结论。

## 更难的对抗样例

```bash
uv run python -m EVA.examples.run_hard_showcase
```

新增六组：精确数量与镜面反射、左右手/道具绑定、遮挡、多区域文字、身份与服装交换冲突、单发饰微编辑、镜面花店编辑。每个结果同时给出分离的动态 VQA、Preservation、PQ、CP/PF、OCR、全项通过率，以及独立 Prompt Advisor 的生图与评审提示词建议，不计算总分。

## 分布外泛化样例

```bash
uv run python -m EVA.examples.run_ood_showcase
```

覆盖微距产品摄影、工笔/蓝图混合、中文信息图、木刻历史场景、风格迁移与材质保持编辑，全部使用分离指标。

## 左右手专项复测

```bash
uv run python -m EVA.examples.probe_hand_evaluation
uv run python -m EVA.examples.probe_hand_positions
```

分别测量自然语言左右手评审与 bbox 坐标法的一致性和误判率。

## Prompt A/B 实际对比

```bash
uv run python -m EVA.examples.run_prompt_ab
uv run python -m EVA.examples.build_prompt_ab_report
```

A 保留原始生成结果，B 使用两阶段 Advisor 的独立改写 Prompt 重新生成；`compare.html` 并排展示两次图片和分离指标，不使用总分。

## 固定原始检查清单复评

```bash
uv run python -m EVA.examples.rescore_prompt_ab_fixed
```

A、B 两组图片均使用原始 Prompt 的同一套检查清单复评，避免修改 Prompt 后评估标准随之变化。

## A/B/C/D/E 连续迭代

```bash
uv run python -m EVA.examples.run_prompt_iterations
uv run python -m EVA.examples.build_prompt_iterations_report
```

保留 A/B，继续生成 C/D/E；每轮使用上一轮图像做独立 Prompt 改写，所有阶段统一用 A 原始检查清单复评，输出 `iterations.html`。"""
