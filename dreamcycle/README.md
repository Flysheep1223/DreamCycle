# DreamCycle HTML 客户端

[English README](README_EN.md)

一个本地 HTML 客户端，用火山方舟 Seedream 和 VLM 完成。整套系统称为 **DreamCycle**，其中的评分与指标协议称为 **DreamIndicators**。

```text
Prompt / 源图
→ 生成 A
→ 多路评审
→ Prompt 改写
→ 生成 B1
→ 最多五轮联合修复
→ 保留最佳候选
```

## 启动

```bash
cd /Users/bytedance/Desktop/Image-indicator
uv sync
uv run uvicorn dreamcycle.server.app:app --host 127.0.0.1 --port 8010
```

打开：

```text
http://127.0.0.1:8010/
```

## 配置

项目根目录 `.env` 保存服务器模型配置：

```text
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
VLM_MODEL=<your-vlm-endpoint>
SEEDREAM_MODEL=<your-seedream-model>
SEEDREAM_SIZE=2K
DREAMER_WORKERS=4
JUDGE_REPEATS=10
```

用户在网页中输入自己的 `ARK_API_KEY`。Key 只用于当次任务，不写入结果文件，也不保存到浏览器。服务器模型 endpoint 必须允许该 key 访问。

可选的私有 TOS 持久化：

```text
TOS_ACCESS_KEY=...
TOS_SECRET_KEY=...
TOS_SESSION_TOKEN=...
TOS_ENDPOINT=tos-cn-beijing.volces.com
TOS_REGION=cn-beijing
TOS_BUCKET=<your-bucket>
TOS_PREFIX=dreamcycle/runs
```

配置完整后，完成的任务及其 A/B 关联运行目录会镜像上传到 TOS。`result.json` 最后上传，避免任务号读到不完整结果。默认 `TOS_DELETE_LOCAL_AFTER_UPLOAD=true`，上传成功后删除本地缓存；设为 `false` 可保留缓存。TOS 失败时仍保留本地结果并在页面提示。图片优先读取本地缓存，本地不存在时通过短期签名 URL 访问私有 TOS 对象。

## ECS 部署

后端可以使用根目录的 `Dockerfile`、`docker-compose.yml` 和 `Caddyfile` 部署到单台 ECS。Caddy 只开放 80/443，内部 Uvicorn 单进程运行在 8010，容器内 `DREAMCYCLE_RUNS_DIR=/tmp/dreamcycle-runs`，TOS 上传成功后自动清理。

```bash
# .env 中按实际部署填写
DREAMCYCLE_DOMAIN=dreamcycle-api.example.com
DREAMCYCLE_CORS_ORIGINS=https://your-miaoda-app.feishuapp.com

# ECS 上启动
docker compose up -d --build
```

同域部署时无需配置跨域。只有前后端分离部署时，才将 `dreamcycle/server/static/config.js` 中的 `window.DREAMCYCLE_API_BASE` 设置为后端 HTTPS 地址，并将 `DREAMCYCLE_CORS_ORIGINS` 设置为实际前端 origin，不使用 `*`。

也可以用 Cloudflare Tunnel 提供受信任的 HTTPS 入口。Quick Tunnel 仅建议用于测试；正式使用建议命名 Tunnel 并配置访问控制。

## 页面功能

- 单个 Prompt 或每行一个 Prompt 的批量任务；
- 运行中继续提交任务，按任务号查找结果；
- 多次累积上传参考图，按文件名自然排序，可单独删除；
- 可选上传已有输出 A；
- 1:1、4:3、3:4、16:9、9:16、3:2、2:3 比例选择；
- A/B 候选横向对比，最终选中的图片自动排在第一位；
- 查看每轮 Prompt、分离指标、逐项理由和结构化证据；
- 任务结果默认同步到私有 TOS，上传成功后清理本地缓存，重启后仍可查询已完成任务。

## 扣分理由与改进

- 当检查项 `score < 0.99` 时，评审必须返回以“扣分点：”开头的具体理由，说明未满足条件、可见缺陷或证据不足；空泛理由会触发纠偏重试。
- `FeedbackPromptRewriter` 和 `TargetedRepairAdvisor` 都会读取失败项的 `reason` 与 `evidence`，据此改写 Prompt 和生成联合修复指令，而不是只根据分数重写。

## 当前验收逻辑

- A 全部通过时直接保留 A，不生成 B；
- A 未全部通过时生成 B1；
- B1 严格成功则停止，否则继续生成 B2–B6；
- 严格成功要求全部检查项达到阈值且受保护指标不退化；
- 未全部通过时保留最佳零退化改善候选，完全并列选择靠后的候选；
- OCR 帕累托约束只使用 F1 和 CER；
- 最低检查项和 NED 仅作诊断，不参与帕累托否决。

## 运行目录

```text
dreamcycle/
├── ark/           # Ark SDK 调用
├── config/        # 环境配置
├── improvement/   # Prompt 改写与多轮优化
├── io/            # 图片和结果存储
├── judge/         # VLM 评审、官方协议与众数聚合
├── ocr/           # RapidOCR 与文字指标
├── pipeline/      # 单图生成和评审流水线
├── reviewer/      # 可选评审建议
├── router/        # 任务路由和检查清单
├── schemas/       # 数据模型
├── dream_indicators/ # DreamIndicators 指标报告与候选选择
├── seedream/      # Seedream 图片生成
├── server/        # FastAPI 后端与 HTML 客户端
├── spatial/       # 分镜和方向动作证据
└── runs/          # 执行期间临时缓存，上传 TOS 后清理
```
