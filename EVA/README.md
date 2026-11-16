# Seedream EVA：生成后实时多路机评

基于火山方舟官方 `arkruntime`，实现 **Seedream 出图 + 多标签路由 + VLM 评审 + OCR + 分离指标报告**。默认读取项目根目录 `.env`，不会打印 API key。

## 已实现

- 文生图、编辑、参考图生成的**多标签路由**，允许混合任务；
- 路由与 Seedream 生图并行，生成后 VLM 与 OCR 并行；
- 动态 task/preservation 检查清单；
- 通用对齐与 PQ，编辑 SC/PQ/Overall，参考图 CP/PF；
- RapidOCR 的 Accuracy、NED、CER、Precision/Recall/F1；
- 逐项检查、全项通过率和最低检查项分，全部保留独立含义与原始尺度；
- 独立 Prompt Advisor 审查全部输入输出与评分理由，给出生成/评审提示词建议；
- 文字内容、位置、重复与额外文字分开评分；镜面实体/倒影区分；源图事实矛盾提前警告；
- 原始输出、路由、逐图分数和汇总结果全部落盘；
- CLI、本地 FastAPI，以及不调用真实 API 的单元测试。

## 环境与启动

```bash
cd /Users/flysheep/Desktop/Image-indicator
uv sync --extra dev
uv run eva config
```

当前 `.env` 变量：

```text
ARK_API_KEY=...
ARK_BASE_URL=...
VLM_MODEL=...
SEEDREAM_MODEL=...
SEEDREAM_SIZE=2K
DREAMER_WORKERS=4
ADVISOR_ENABLED=true
```

## CLI

```bash
# 只测试多标签路由
uv run eva route \
  --prompt '一张简洁中文海报，标题为春日咖啡' \
  --target-text '春日咖啡'

# 真实生成并实时评分
uv run eva run \
  --prompt '一张简洁中文海报，标题为春日咖啡' \
  --target-text '春日咖啡'

# 带源图/参考图生成
uv run eva run \
  --prompt '保留主体，把背景换成月球，并加上 MOON 字样' \
  --image /absolute/path/source.png \
  --target-text 'MOON'

# 不调用 Seedream，只评已有图片
uv run eva run \
  --prompt '一张橘猫坐在窗边的照片' \
  --generated-image /absolute/path/generated.png

# 关闭独立 Prompt Advisor，减少一次 VLM 调用
uv run eva run --prompt '一张猫的照片' --no-advice
```

每次输出一个目录：

```text
EVA/runs/run-.../
├── request.json
├── generation.json       # 新生成时存在
├── route.json
├── generated-00.png
├── judge-00.json         # VLM原始结构
├── advice-00.json        # 独立Prompt与评审建议（启用时）
├── score-00.json         # 分离指标与原始证据
└── result.json           # 全量结果
```

## 本地实时 API

```bash
uv run uvicorn EVA.server.app:app --host 127.0.0.1 --port 8000
```

```bash
curl -X POST http://127.0.0.1:8000/v1/evaluate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "一张写着春日咖啡的中文海报",
    "input_images": [],
    "target_texts": ["春日咖啡"]
  }'
```

仅建议绑定 `127.0.0.1`：当前输入支持本地路径与任意图片 URL，属于受信任的本地开发接口。

## 模块索引

| 模块 | 职责 |
|---|---|
| `config/` | `.env`、模型、并发和非敏感配置 |
| `schemas/` | 路由、评审、OCR 和结果的类型契约 |
| `ark/` | 官方 Ark SDK 的视觉结构化输出与图片生成 |
| `seedream/` | 图片生成、下载与生成参数落盘 |
| `router/` | 多标签意图、规则校验、低置信并集 |
| `judge/` | 单次 VLM 通用/编辑/参考图评审 |
| `ocr/` | RapidOCR 适配和独立文本指标 |
| `scoring/` | 分离指标报告，不计算总分或跨指标归一化 |
| `reviewer/` | 独立审计所有图像/分数/理由，输出生成与评审提示词建议 |
| `pipeline/` | 生成/路由和评分/OCR 的异步编排 |
| `server/` | 本地 FastAPI 接口 |
| `cli/` | `eva config/route/run` 命令 |
| `io/` | 图片 data URI、下载与运行目录 |
| `tests/` | 不访问网络的单元与流程测试 |

每个模块的职责说明已内嵌在对应 `__init__.py` 的模块 docstring 中，不再单独维护模块级 `README.md`。

## 评分口径

**不再计算 `custom_overall`、`strict_overall`、权重或跨指标归一化分。** 输出 Task、Preservation、PQ、编辑 SC/PQ、参考图 CP/PF、OCR、逐项检查和全项通过率，各自保留原始尺度。任意用户 Prompt 的 QA 是动态生成的；官方固定 benchmark 与 Vendi/FID 等集合指标应放在离线层。

当前 MVP 不含独立 DINO/CLIP embedding、mask 背景指标及 mIoU/OKS/mAP 专用控制模型。控制要求可进入动态 VLM 清单，结果中会明确标注专用模型尚未启用。

## 复杂真实样例

```bash
uv run python -m EVA.examples.run_showcase

# 更难的对抗样例：精确数量、遮挡、镜面、多区域文字与小编辑
uv run python -m EVA.examples.run_hard_showcase

# 分布外泛化：微距产品、工笔蓝图、信息图、木刻与风格迁移
uv run python -m EVA.examples.run_ood_showcase
```

脚本先运行两个超复杂原创二次元文生图，再复用输出图执行单参考、双参考和两个限定编辑任务。父目录 `EVA/runs/showcase-*/summary.json` 汇总六个案例；每个案例的完整图片、路由、原始评审和分数仍在各自的 `run-*` 子目录中。

## 结果预览（图片与文字直接嵌入）

### 超复杂二次元文生图

![雨夜赛博神社示例](runs/run-20261115T101304-7dbcbd0f/generated-00.png)

该样例动态 VQA 为 0.962，PQ=9.0，OCR Accuracy=1.0。VLM 不只检查整体风格，还逐项检查三名角色、石狐、纸鹤位置、列车和招牌文字；纸鹤的前景/中景区别被单独扣分。

### 高难度镜面花店

![镜面花店示例](runs/run-20261115T112951-e6f3d43a/generated-00.png)

该样例动态 VQA 为 0.583，PQ=6.0，全项通过率为 28.57%。主要问题包括左右手持物、玫瑰数量、重复 LEFT、镜面反射范围和遮挡关系。Prompt Advisor 还指出主评审曾把镜中倒影误算成额外人物，因此评测提示词已增加“现实实体与倒影分开”的规则。

### 文档阅读说明

- `SHOWCASE_RESULTS.md`：直接嵌入普通六组样例图片、分数与失败原因；
- `HARD_SHOWCASE_RESULTS.md`：直接嵌入高难度图片、分离指标和 Prompt Advisor 建议；
- `EVALUATION_FIXES.md`：直接嵌入问题图片和修正后的实际验证结果；
- `OOD_RESULTS.md`：直接嵌入分布外 Prompt、参考图、结果图、分离指标及两阶段审计意见。

阅读这些结果不再依赖“图片/分数/建议”的 JSON 跳转链接；JSON 仅作为原始数据保留。

## 测试

```bash
uv run pytest -q
uv run ruff check EVA
```

真实联通测试使用一张简单中文海报，避免把示例输出当作公开 benchmark 结论。复杂样例也只用于验证系统运行与失败定位，不构成统计性模型质量结论。
