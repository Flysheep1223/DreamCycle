# DreamCycle HTML Client

[中文 README](README.md)

DreamCycle is an HTML client for Seedream image generation and VLM evaluation. The complete product is called **DreamCycle**, and its evaluation and metrics protocol is called **DreamIndicators**.

```text
Prompt / source image
→ generate A
→ multi-protocol evaluation
→ prompt rewriting
→ generate B1
→ up to five joint repair rounds
→ keep the best candidate
```

## Quick start

```bash
uv sync
uv run uvicorn dreamcycle.server.app:app --host 127.0.0.1 --port 8010
```

Open:

```text
http://127.0.0.1:8010/
```

## Configuration

The project-level `.env` stores server model configuration:

```text
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
VLM_MODEL=<your-vlm-endpoint>
SEEDREAM_MODEL=<your-seedream-model>
SEEDREAM_SIZE=2K
DREAMER_WORKERS=4
JUDGE_REPEATS=10
```

Users enter their own `ARK_API_KEY` in the browser. The key is used only for that task and is not written to result files or browser storage. The configured model endpoints must be accessible to that key.

Optional private TOS persistence:

```text
TOS_ACCESS_KEY=...
TOS_SECRET_KEY=...
TOS_SESSION_TOKEN=...
TOS_ENDPOINT=tos-cn-beijing.volces.com
TOS_REGION=cn-beijing
TOS_BUCKET=<your-bucket>
TOS_PREFIX=dreamcycle/runs
TOS_DELETE_LOCAL_AFTER_UPLOAD=true
```

When these settings are complete, each completed job and its related A/B run directories are uploaded to TOS. `result.json` is uploaded last to avoid incomplete results being read. Local caches are deleted after a successful upload. Set `TOS_DELETE_LOCAL_AFTER_UPLOAD=false` to retain them. If TOS upload fails, the local result is retained and the page shows a warning.

Images are served from the local cache when available, or through short-lived signed URLs for private TOS objects.

## Features

- Submit a single Prompt;
- Submit more jobs while other jobs are running, and look up jobs by ID;
- Upload multiple reference images over multiple selections, naturally sorted by filename and individually removable;
- Optionally provide an existing output A;
- Choose 1:1, 4:3, 3:4, 16:9, 9:16, 3:2, or 2:3 aspect ratios;
- Compare A/B candidates in a horizontal strip, with the selected candidate moved to the front;
- Inspect per-round Prompts, separated metrics, deduction reasons, and structured evidence;
- Store completed results in private TOS and keep them searchable after a restart.

## Deduction reasons and improvement

- When a check scores below `0.99`, the judge is encouraged to return a concrete reason and evidence. Missing reasons no longer block evaluation or trigger a mandatory retry.
- `FeedbackPromptRewriter` and `TargetedRepairAdvisor` receive the failed checks, their `reason`, and their `evidence`. They use these concrete defects to rewrite Prompts and generate joint repair instructions, rather than reacting only to numeric scores.

## Acceptance and base-image selection

- If A already passes all required checks, keep A and do not generate B;
- Otherwise, generate B1 from the original inputs, then evaluate it with A's route and checklist;
- If B1 strictly succeeds, stop. Otherwise, generate B2–B6 with up to five joint repair rounds;
- Each repair round addresses all currently repairable failures while preserving passed and improved checks;
- Later repairs use the current viable base image. If the latest candidate has no repair potential, retain the previous viable base. If B1 is not viable, the first repair starts from A;
- Strict success requires all required checks to pass and no protected metric to regress while at least one protected metric improves;
- If no candidate fully succeeds, keep the best no-regression improvement. Exact ties go to the later candidate;
- OCR acceptance uses only F1 and CER. Minimum check score and NED remain diagnostic and do not independently veto a candidate.

## Metrics

- **Dynamic VQA (`task_score`)**: mean score of task and preservation checks, from 0 to 1;
- **G-PQ**: general perceptual quality, from 0 to 10;
- **Edit SC**: `min(edit_success, overedit_control)`;
- **Edit E-PQ**: `min(naturalness, artifact_free)`;
- **Edit Overall**: `sqrt(SC × E-PQ)`, used only as a derived editing metric;
- **Reference CP/PF**: concept preservation and prompt following, each from 0 to 4;
- **Reference CPPF**: `CP × PF`, from 0 to 16, used for reference-candidate comparison;
- **OCR**: F1 for exact-line matching and CER for character-level errors;
- **Full requirement rate and minimum check score**: separate checklist statistics. The minimum score is diagnostic and is not a Pareto veto.

Metrics remain separated; there is no weighted cross-metric total score.

## Deployment

Use the root `Dockerfile`, `docker-compose.yml`, and `Caddyfile` on a single ECS instance. Caddy exposes 80/443. Uvicorn runs as one process on port 8010 inside the container network. Set:

```text
DREAMCYCLE_RUNS_DIR=/tmp/dreamcycle-runs
DREAMCYCLE_DOMAIN=dreamcycle-api.example.com
DREAMCYCLE_CORS_ORIGINS=
```

Then run:

```bash
docker compose up -d --build
```

No CORS configuration is needed for same-origin deployment. For a split frontend/backend deployment, set `window.DREAMCYCLE_API_BASE` in `dreamcycle/server/static/config.js` to the backend HTTPS origin and configure `DREAMCYCLE_CORS_ORIGINS` with the actual frontend origin. Do not use `*`.

Cloudflare Tunnel is also supported for trusted HTTPS access. Quick Tunnels are intended for testing only; use a named tunnel with access control for production.

## Project layout

```text
dreamcycle/
├── ark/              # Ark SDK integration
├── config/           # Environment settings
├── improvement/      # Prompt rewriting and multi-round optimization
├── io/               # Image and result storage
├── judge/            # VLM judging, official protocols, and modal aggregation
├── ocr/              # RapidOCR and text metrics
├── pipeline/         # Per-image generation and evaluation pipeline
├── reviewer/         # Optional review advisor
├── router/           # Task routing and checklists
├── schemas/          # Shared data models
├── dream_indicators/ # Metric reporting and candidate selection
├── seedream/         # Seedream image generation
├── server/           # FastAPI backend and HTML client
├── spatial/          # Storyboard and directional-action evidence
└── runs/             # Temporary working cache, removed after TOS upload
```
