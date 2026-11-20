# DreamCycle & DreamIndicators

DreamCycle is a generate–evaluate–rewrite–accept framework for Seedream. It combines multi-label routing, explainable image evaluation, and prompt optimization while protecting already-satisfied requirements from regression.

- **DreamCycle** handles image generation, feedback rewriting, joint repairs, base-image inheritance, and best-candidate selection.
- **DreamIndicators** handles dynamic checklists, VLM/OCR evaluation, structured evidence, metric aggregation, and acceptance rules.

For the HTML client guide, see [DreamCycle HTML Client](dreamcycle/README_EN.md).

## Core loop

The original Prompt and A's evaluation ruler remain fixed:

```text
Generate an image
→ inspect requirements and task-specific metrics
→ collect concrete failure evidence
→ rewrite or jointly repair
→ generate again
→ evaluate against the original A
```

The system does not simply return the last image:

- **A already passes**: keep A and stop without generating B;
- **A candidate strictly succeeds**: accept it and stop early;
- **Only partial improvement is available after all rounds**: keep the best no-regression improvement;
- **No valid improvement exists**: fall back to A rather than changing the image for its own sake.

## Main features

- **Multi-label task routing**: text-to-image, image editing, reference generation, and mixed tasks. OCR can be enabled as an additional evaluation path.
- **Dynamic VQA**: generate checks for objects, attributes, counts, positions, relationships, style, and text from the Prompt.
- **Official protocols plus project extensions**: VIEScore editing sub-scores and DreamBench++ CP/PF evaluation.
- **Concrete deduction reasons when available**: low scores are encouraged to include specific `扣分点：` reasons and evidence. Missing or vague reasons no longer block evaluation or trigger mandatory retries.
- **Repeated evaluation aggregation**: ten independent VLM evaluations by default, using per-field modes with the lower score on ties.
- **Independent OCR**: RapidOCR runs once and is kept separate from VLM layout evaluation.
- **Best checkpoints and no-regression acceptance**: candidates are always compared with original A, not just with the previous round.
- **Local and private-cloud results**: Prompts, routes, images, raw evaluations, metrics, and acceptance records can be mirrored to private TOS.
- **HTML client and Python modules**: single-Prompt tasks, reference-image upload, existing-A input, and A/B comparison.

## Architecture

### Single-image generation and evaluation

```text
Original Prompt + input images + target texts
        │
        ├── Multi-label routing → task types, checklists, evidence requirements
        │
        └── Seedream generates A, or an existing image is used
                    │
                    ├── Generic VLM judge
                    ├── VIEScore SC / E-PQ for editing
                    ├── DreamBench++ CP / PF for references
                    └── RapidOCR when target text exists
                    │
                    └── Per-field modal aggregation and derived metrics
```

Routing and generation run in parallel when a new image is needed. VLM and OCR run in parallel where applicable. Official editing and reference evaluation requests are also issued independently.

With generic, editing, and reference evaluation enabled, one independent review can contain five VLM requests. Ten repetitions produce 50 requests, plus directional-action requests when applicable. Set `JUDGE_REPEATS=1` for lower-cost debugging.

### Multi-round optimization

```text
Fixed A baseline
    │
    ├── A already passes → keep A
    │
    └── Otherwise → B1 from original inputs
                    │
                    ├── Strict success → stop and accept
                    │
                    └── Otherwise → B2–B6 joint repairs
                                      │
                                      ├── Best no-regression improvement → keep it
                                      └── No valid improvement → retain A
```

B1 uses a rewritten complete Prompt from the original inputs. Later repairs use local editing instructions against the current viable base image. If the latest candidate has no repair potential, the previous viable base is retained; if B1 is not viable, the first repair starts from A.

Every re-evaluation uses the original Prompt and A's fixed route. Repair instructions never become a new scoring ruler.

## DreamIndicators

| Dimension | Field | Scale and purpose |
|---|---|---|
| Task alignment | `task_score` | 0–1; mean score of task checks |
| General perceptual quality | `g_pq` | 0–10; naturalness, structural anomalies, artifacts, and local fusion |
| Text layout | `text_layout_score` | 0–1 or null; carrier, position, duplication, and specified layout |
| OCR | `accuracy`, `ned`, `cer`, `precision`, `recall`, `f1` | Original definitions, kept separate from layout |
| Edit success | `edit.sc` | 0–10; `min(edit_success, overedit_control)` |
| Edit perceptual quality | `edit.e_pq` | 0–10; `min(naturalness, artifact_free)` |
| Edit overall | `edit.overall` | 0–10; `sqrt(SC × E-PQ)`, used only inside editing |
| Concept preservation | `reference.cp` | 0–4; preservation of the reference subject or concept |
| Prompt following | `reference.pf` | 0–4; completion of the new scene and instructions |
| Reference joint metric | `reference.cppf` | 0–16; `CP × PF`, used for reference acceptance |
| Full requirement rate | `full_requirement_rate` | 0–1; fraction of checks scoring at least 0.90 |
| Minimum check score | `minimum_requirement_score` | 0–1; diagnostic minimum across checks |

Fields that do not apply are `null`, not zero. There is no weighted cross-metric total score beyond the editing Overall and reference CPPF.

### Dynamic VQA

The router breaks a Prompt into concrete checks. The VLM scores each check from 0 to 1 and returns a reason and structured evidence. Ten independent reviews are aggregated per field using the mode, with the lower score on ties:

```text
task_score = Σ task_check_scores / number_of_task_checks
```

Preservation checks remain separate rather than being collapsed into a `preservation_score`, but they still contribute to full requirement rate and minimum-check statistics.

### G-PQ and editing metrics

G-PQ is a project-defined general VLM quality score, not a Q-Align model output or a distribution over Q-Align quality labels.

Editing uses VIEScore's four sub-scores and per-image formulas:

```text
SC      = min(edit_success, overedit_control)
E-PQ    = min(naturalness, artifact_free)
Overall = sqrt(SC × E-PQ)
```

SC and E-PQ are derived after repeated sub-score aggregation. Edit Overall is not combined with G-PQ, OCR, dynamic VQA, or CP/PF.

### Text evaluation

Text evaluation has two evidence paths:

- **RapidOCR** runs once, applies Unicode NFKC and whitespace normalization, matches targets one-to-one, and computes Accuracy, NED, CER, Precision, Recall, and F1.
- **VLM layout evaluation** checks carrier, position, duplication, and specified layout, aggregated across ten reviews by default.

Perfect OCR does not imply correct placement or typography. Extra OCR lines increase false positives; layout is penalized for extra text only when the user explicitly forbids it.

### Reference CP / PF / CPPF

- **CP (Concept Preservation)**: preservation of subject identity or concept, from 0 to 4.
- **PF (Prompt Following)**: adherence to the new Prompt, from 0 to 4.
- **CPPF**: `CP × PF`, from 0 to 16, used for reference-candidate comparison.

High CP does not imply high PF: copying the reference may preserve the subject while failing the new task.

### Checklist statistics

```text
full_requirement_rate = checks scoring ≥ 0.90 / all checks
minimum_requirement_score = minimum score across all checks
```

Both task and preservation checks contribute to these statistics. Full requirement rate participates in acceptance; minimum check score and OCR NED remain diagnostic and do not independently veto candidates.

## Acceptance and base-image inheritance

Strict success requires all three conditions:

1. Every task and preservation check reaches `0.90`;
2. At least one protected metric improves over original A;
3. No protected metric regresses.

Protected metrics currently include:

| Category | Fields |
|---|---|
| Task | `task_score` |
| General quality | `g_pq` |
| Text layout | `text_layout_score` |
| Full requirement rate | `full_requirement_rate` |
| OCR | Only `ocr.cer` (lower is better) and `ocr.f1` (higher is better) |
| Editing | Only `edit.sc` and `edit.e_pq` |
| References | Only `reference.cppf` |

Minimum check score, OCR NED, the four editing sub-scores, CP, and PF do not independently veto a candidate; they remain available for diagnosis.

A candidate may become the next repair base only when it has at least one checklist improvement and no more degradations than improvements over A. Being a viable repair base does not imply strict acceptance.

If no candidate fully succeeds, the best no-regression improvement is retained. Exact ties go to the later candidate. If no such candidate exists, A is retained.

## Quick start

```bash
uv sync
uv run uvicorn dreamcycle.server.app:app --host 127.0.0.1 --port 8010
```

Open:

```text
http://127.0.0.1:8010/
```

The HTML client supports:

- Single-Prompt tasks;
- Existing output A input;
- Multiple reference images accumulated across selections, naturally sorted by filename and individually removable;
- Aspect-ratio selection and automatic size mapping;
- Horizontal A/B candidate comparison with the selected image moved first;
- Per-round Prompts, separated metrics, deduction reasons, and structured evidence;
- Job lookup by ID.

## Configuration

The project `.env` stores model and storage settings:

```text
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
VLM_MODEL=<your-vlm-endpoint>
SEEDREAM_MODEL=<your-seedream-model>
SEEDREAM_SIZE=2K
DREAMER_WORKERS=4
JUDGE_REPEATS=10
```

Users enter their own `ARK_API_KEY` in the browser. Keys are used only for that task and are not written to result files or browser storage. The configured model endpoints must be accessible to that key.

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

Completed jobs and related A/B directories are uploaded to TOS, with `result.json` uploaded last. Local caches are deleted after a successful upload. If upload fails, local results are retained and the page shows a warning. Images use local cache when present, or short-lived signed URLs for private TOS objects.

## Deployment

Use the root `Dockerfile`, `docker-compose.yml`, and `Caddyfile` on a single ECS instance. Caddy exposes 80/443, while Uvicorn runs as one process on port 8010 inside the container network:

```bash
docker compose up -d --build
```

Set:

```text
DREAMCYCLE_RUNS_DIR=/tmp/dreamcycle-runs
DREAMCYCLE_DOMAIN=dreamcycle-api.example.com
DREAMCYCLE_CORS_ORIGINS=
```

No CORS configuration is needed for same-origin deployment. For a split frontend/backend deployment, set `window.DREAMCYCLE_API_BASE` in `dreamcycle/server/static/config.js` to the backend HTTPS origin and set `DREAMCYCLE_CORS_ORIGINS` to the actual frontend origin, not `*`.

Cloudflare Tunnel is also supported for trusted HTTPS access. Quick Tunnels are intended for testing; use a named tunnel with access control for production.

## Project structure

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

## Boundaries and references

- Dynamic VQA is a project-specific checklist-based metric, not official VQAScore.
- G-PQ is not a Q-Align model output.
- Editing metrics use VIEScore-style sub-scores and formulas, but do not claim reproduction of an official leaderboard result.
- DreamBench++ CP/PF follows the official evaluation templates, while repetition and modal aggregation are project extensions.
- Model scores are review evidence, not absolute ground truth; important cases should still be inspected manually.

For the client-focused guide, see [DreamCycle HTML Client](dreamcycle/README_EN.md).
