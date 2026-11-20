"""Local FastAPI backend for the DreamCycle HTML client."""

from __future__ import annotations

import base64
import binascii
import json
import re
from dataclasses import replace
from pathlib import Path, PurePosixPath

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from dreamcycle.config import get_settings
from dreamcycle.server.jobs import Job, JobManager


class ImagePayload(BaseModel):
    filename: str
    data: str


class JobRequest(BaseModel):
    api_key: str = Field(min_length=1, repr=False)
    prompt: str = Field(min_length=1)
    input_images: list[ImagePayload] = Field(default_factory=list)
    generated_image: ImagePayload | None = None
    target_texts: str = ""
    generation_size: str = ""
    aspect_ratio: str | None = None
    generation_seed: int | None = None


app = FastAPI(title="DreamCycle HTML Client", version="0.3.0")
settings = get_settings()
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[item.strip() for item in settings.cors_origins.split(",") if item.strip()],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
job_manager = JobManager(settings)
static_dir = Path(__file__).with_name("static")
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
ALLOWED_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
ASPECT_RATIO_SIZES = {
    "1:1": "2048x2048",
    "4:3": "2304x1728",
    "3:4": "1728x2304",
    "16:9": "2560x1440",
    "9:16": "1440x2560",
    "3:2": "2496x1664",
    "2:3": "1664x2496",
}


@app.get("/", include_in_schema=False)
@app.get("/ui", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/health", include_in_schema=False)
def health() -> dict:
    return {"status": "ok", "settings": settings.public_dict()}


@app.get("/v1/config", include_in_schema=False)
def config() -> dict:
    return {
        "settings": settings.public_dict(),
        "judge_repeats": settings.judge_repeats,
        "max_repairs": 5,
        "upload_limit_mb": MAX_UPLOAD_BYTES // (1024 * 1024),
    }


@app.get("/runs/{path:path}", include_in_schema=False)
def run_file(path: str):
    relative = PurePosixPath(path)
    if relative.is_absolute() or ".." in relative.parts:
        raise HTTPException(status_code=404, detail="文件不存在")
    local_path = (settings.runs_dir / relative.as_posix()).resolve()
    if not local_path.is_relative_to(settings.runs_dir.resolve()):
        raise HTTPException(status_code=404, detail="文件不存在")
    if local_path.is_file():
        return FileResponse(local_path)
    if job_manager.tos.enabled:
        try:
            return RedirectResponse(job_manager.tos.signed_url(relative.as_posix()))
        except Exception as exc:
            raise HTTPException(status_code=503, detail="TOS 文件暂时无法访问") from exc
    raise HTTPException(status_code=404, detail="文件不存在")


def save_upload(job: Job, upload: ImagePayload, name: str) -> str:
    suffix = Path(upload.filename).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail=f"不支持的图片格式：{suffix or '无扩展名'}")
    try:
        content = base64.b64decode(upload.data, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=400, detail="图片 Base64 编码无效") from exc
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail=f"{upload.filename} 超过 25MB 限制")
    if not content:
        raise HTTPException(status_code=400, detail=f"{upload.filename} 是空文件")
    destination = job.run_dir / "inputs" / f"{name}{suffix}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return str(destination)


@app.post("/v1/jobs", status_code=202, include_in_schema=False)
async def create_job(payload: JobRequest) -> dict:
    job = job_manager.create()
    try:
        sources = [
            save_upload(job, upload, f"source_{index:02d}")
            for index, upload in enumerate(payload.input_images)
        ]
        existing_a = (
            save_upload(job, payload.generated_image, "existing_a")
            if payload.generated_image
            else None
        )
    except HTTPException as exc:
        job.status = "failed"
        job.error = str(exc.detail)
        raise
    if payload.aspect_ratio and payload.aspect_ratio not in ASPECT_RATIO_SIZES:
        raise HTTPException(status_code=400, detail="不支持的图片比例")
    texts = [item.strip() for item in re.split(r"[\n,，]+", payload.target_texts) if item.strip()]
    case = {
        "case": job.id,
        "title": "用户优化任务",
        "prompt": payload.prompt.strip(),
        "input_images": sources,
        "target_texts": texts,
        "image": existing_a,
        "size": payload.generation_size.strip()
        or ASPECT_RATIO_SIZES.get(payload.aspect_ratio or "", settings.seedream_size),
        "seed": payload.generation_seed if payload.generation_seed is not None else 20261117,
    }
    job.prompt = payload.prompt.strip()
    caller_key = payload.api_key.strip()
    if not caller_key:
        raise HTTPException(status_code=400, detail="ARK API Key 不能为空")
    request_settings = replace(settings, ark_api_key=caller_key)
    job_manager.start(job, case, request_settings)
    return job.public()


def get_job_or_404(job_id: str) -> Job:
    job = job_manager.get(job_id)
    if job is not None:
        return job
    if not re.fullmatch(r"[A-Za-z0-9_-]+", job_id):
        raise HTTPException(status_code=404, detail="任务不存在")
    run_dir = settings.runs_dir / job_id
    result_path = run_dir / "result.json"
    if result_path.is_file():
        result = json.loads(result_path.read_text(encoding="utf-8"))
        return Job(
            id=job_id,
            run_dir=run_dir,
            status="done",
            message="完成",
            prompt=result.get("original", {}).get("prompt", ""),
            result=result,
        )
    if job_manager.tos.enabled:
        try:
            result = job_manager.tos.read_job_result(job_id)
        except Exception as exc:
            raise HTTPException(status_code=503, detail="TOS 结果暂时无法读取") from exc
        if result is not None:
            return Job(
                id=job_id,
                run_dir=run_dir,
                status="done",
                message="完成",
                prompt=result.get("original", {}).get("prompt", ""),
                result=result,
            )
    raise HTTPException(status_code=404, detail="任务不存在或服务已重启")


@app.get("/v1/jobs/{job_id}", include_in_schema=False)
def job_status(job_id: str) -> dict:
    return get_job_or_404(job_id).public()


@app.get("/v1/jobs/{job_id}/result", include_in_schema=False)
def job_result(job_id: str) -> dict:
    job = get_job_or_404(job_id)
    if job.status != "done" or job.result is None:
        raise HTTPException(status_code=409, detail="任务尚未完成")
    return job.result
