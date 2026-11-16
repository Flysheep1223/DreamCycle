# 实时机评路由器：内部工作流

> 路由器只负责决定**这次需要运行哪些评分器、准备哪些检查项**，不负责给图片打分。它与 Seedream 生图并行，输出一份结构化“评分计划”。

## 一、路由工作流图

![Seedream 实时机评多标签路由工作流：输入盘点、规则初筛、意图识别、冲突校验、检查清单和评分计划](15_Router_Workflow.svg)

[打开或下载原始 SVG 矢量图](15_Router_Workflow.svg)（可无限缩放，也可用矢量编辑软件继续修改）

## 二、每一步具体做什么？

### ① 输入盘点

整理结构化输入，而不是直接把整段请求扔给评分器：

```json
{
  "prompt": "保留这只狗，把背景换成月球，并加上 MOON 字样",
  "input_image_count": 1,
  "input_images": [{"role": "unknown", "image_id": "img_0"}],
  "explicit_control": null
}
```

此阶段只确认“用户给了什么”，不判断输出效果。

### ② 确定性规则初筛

优先使用简单、稳定的规则：

- 没有输入图：通常是 `text_to_image`，不启用编辑和参考图保持；
- 有输入图：保留 `image_editing` 与 `reference_generation` 的可能；
- Prompt 含明确标题、招牌、日期、数字等：设置 `needs_ocr=true`；
- 有多张参考图：设置 `multi_reference=true`；
- 有姿态、分割、深度等结构化条件：设置 `needs_control=true`。

OCR、控制条件是**可叠加标签**，不与三个主任务互斥。

### ③ VLM/LLM 意图识别

模型只回答“要修改源图，还是把图作为参考，抑或两者都有”。

系统提示词示例：

```text
你是图像生成任务路由器，不负责图像质量评分。

根据原始 Prompt、输入图片及输入角色，判断：
1. 是否是纯文生图；
2. 是否要求修改已有源图；
3. 是否要求保持参考主体、身份或风格并生成新内容；
4. 是否包含需要 OCR 验证的目标文字；
5. 是否包含多个参考主体或显式控制条件。

允许多个主任务同时成立。若编辑与参考保持无法区分，返回两者，不要强行单选。
只输出指定 JSON。
```

### ④ 多标签 JSON

```json
{
  "modes": ["image_editing", "reference_generation"],
  "needs_ocr": true,
  "needs_control": false,
  "multi_reference": false,
  "confidence": 0.91,
  "reason": "既要求改变源图背景，又要求保持原主体，并指定 MOON 文字"
}
```

`confidence` 只用于路由决策，不是图像效果分。

### ⑤ Schema 与冲突校验

在调用评分插件前检查：

- `image_editing`、`reference_generation` 是否有对应输入图；
- `multi_reference=true` 是否与参考图数量一致；
- OCR 是否有目标字符串或明确的文字区域要求；
- 控制指标是否有对应的控制条件；
- 是否误把可叠加标签当成互斥类别。

不能只靠模型返回的文本直接执行，必须经过程序校验。

### ⑥ 低置信与混合意图怎么处理？

推荐策略：

```text
明确命中       → 只运行命中的插件
混合任务       → 运行所有实际命中的插件
低置信但有两种合理解释 → 两路都跑
```

例如“让这个角色在这个场景里更自然”可能既有编辑，也有主体参考要求。两路都跑通常比错误地只跑一路更稳妥。

### ⑦ 生成评分计划

```json
{
  "always_run": ["generic_alignment_vlm", "perceptual_quality_vlm"],
  "plugins": ["edit_sc_pq", "reference_cp_pf", "ocr"],
  "checklists": {
    "task": [
      "背景是否变为月球？",
      "是否出现且仅出现目标文字 MOON？"
    ],
    "preservation": [
      "是否保留参考狗的身份特征？",
      "未要求改变的构图内容是否保持？"
    ]
  }
}
```

这份计划在 Seedream 生图期间完成。图片返回后，直接按计划并行执行，不再临时决定指标。

## 三、路由器与评分器的关系

```text
路由器输出：要评什么、运行哪些插件、检查项是什么
评分器输出：每个检查项得多少分、PQ 多少、具体失败原因
聚合器输出：当前任务实际适用的分项结果
```

三者不要合并成一个巨大的提示词。否则任务分类、指标选择和分数计算会互相污染，难以排查问题。

## 四、推荐的最简路由伪代码

```text
inventory = inspect_inputs(prompt, input_images, controls)
route = normalize(router_vlm(inventory))
route = validate_against_inputs(route, inventory)

plugins = {generic_alignment, perceptual_quality}

if text_to_image in route.modes:
    plugins += dynamic_atomic_alignment

if image_editing in route.modes:
    plugins += edit_sc_pq

if reference_generation in route.modes:
    plugins += reference_cp_pf

if route.needs_ocr:
    plugins += ocr

if route.needs_control:
    plugins += condition_specific_metrics

if route.low_confidence:
    plugins = union(plugins, all_plausible_plugins(route))

plan = build_checklists(route, plugins)
return plan
```

**核心原则：通用评分始终执行，专项评分按多标签并集执行；路由低置信时扩大覆盖，而不是随意单选。**
