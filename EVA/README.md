# Seedream EVA HTML 客户端

一个本地 HTML 客户端，用火山方舟 Seedream 和 VLM 完成：

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
uv run uvicorn EVA.server.app:app --host 127.0.0.1 --port 8010
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
TOS_PREFIX=eva/runs
```

配置完整后，完成的任务及其 A/B 关联运行目录会镜像上传到 TOS。`result.json` 最后上传，避免任务号读到不完整结果。默认 `TOS_DELETE_LOCAL_AFTER_UPLOAD=true`，上传成功后删除本地缓存；设为 `false` 可保留缓存。TOS 失败时仍保留本地结果并在页面提示。图片优先读取本地缓存，本地不存在时通过短期签名 URL 访问私有 TOS 对象。

## ECS＋妙搭部署

后端可以使用根目录的 `Dockerfile`、`docker-compose.yml` 和 `Caddyfile` 部署到单台 ECS。Caddy 只开放 80/443，内部 Uvicorn 单进程运行在 8010，容器内 `EVA_RUNS_DIR=/tmp/eva-runs`，TOS 上传成功后自动清理。

```bash
# .env 中按实际部署填写
EVA_DOMAIN=eva-api.example.com
EVA_CORS_ORIGINS=https://your-miaoda-app.feishuapp.com

# ECS 上启动
docker compose up -d --build
```

妙搭托管前端时，将 `EVA/server/static/config.js` 中的 `window.EVA_API_BASE` 设置为 ECS 的 HTTPS 地址，例如 `https://eva-api.example.com`。默认空字符串表示同域访问。`EVA_CORS_ORIGINS` 只填写实际妙搭前端 origin，不填写后端域名，也不使用 `*`。

## 页面功能

- 单个 Prompt 或每行一个 Prompt 的批量任务；
- 运行中继续提交任务，按任务号查找结果；
- 多次累积上传参考图，按文件名自然排序，可单独删除；
- 可选上传已有输出 A；
- 1:1、4:3、3:4、16:9、9:16、3:2、2:3 比例选择；
- A/B 候选横向对比，最终选中的图片自动排在第一位；
- 查看每轮 Prompt、分离指标、逐项理由和结构化证据；
- 任务结果保存在 `EVA/runs/`，重启后仍可查询已完成任务。

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
EVA/
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
├── scoring/       # 指标报告与候选选择
├── seedream/      # Seedream 图片生成
├── server/        # FastAPI 后端与 HTML 客户端
├── spatial/       # 分镜和方向动作证据
└── runs/          # 本地任务结果（保留）
```
