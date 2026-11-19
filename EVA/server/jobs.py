"""In-memory job coordination for the local browser UI."""

from __future__ import annotations

import asyncio
import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from EVA.ark import ArkClient
from EVA.config import Settings, get_settings
from EVA.improvement import SimpleImprovementService, TargetedRepairAdvisor
from EVA.improvement.optimization import optimize_case
from EVA.io.storage import create_run_dir, write_json
from EVA.io.tos_storage import TosStorage


@dataclass
class Job:
    id: str
    run_dir: Path
    status: str = "queued"
    message: str = "等待开始"
    prompt: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    result: dict[str, Any] | None = None
    error: str | None = None

    def public(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status,
            "message": self.message,
            "prompt": self.prompt,
            "created_at": self.created_at,
            "output_dir": str(self.run_dir),
            "result": self.result,
            "error": self.error,
        }


def friendly_job_error(exc: Exception) -> str:
    if "InputTextSensitiveContentDetected" in str(exc):
        return "Ark 内容审核未通过：请修改或简化 Prompt 后重新提交。本次未生成图片。"
    return f"{type(exc).__name__}: {exc}"


def result_run_directories(job: Job, result: dict[str, Any], runs_dir: Path) -> list[Path]:
    directories = {job.run_dir.resolve()}
    stages = [result.get("original", {}), *result.get("attempts", [])]
    first = result.get("first", {})
    stages.extend([first.get("a") or {}, first.get("b") or {}])
    for stage in stages:
        output_dir = stage.get("output_dir")
        if not output_dir:
            continue
        path = Path(output_dir).resolve()
        if path.is_dir() and path.is_relative_to(runs_dir.resolve()):
            directories.add(path)
    return sorted(directories)


class JobManager:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.tos = TosStorage(self.settings)
        self.jobs: dict[str, Job] = {}
        self.tasks: set[asyncio.Task] = set()

    def create(self) -> Job:
        run_id, run_dir = create_run_dir(self.settings.runs_dir, prefix="web-job")
        job = Job(id=run_id, run_dir=run_dir)
        self.jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        return self.jobs.get(job_id)

    def start(
        self, job: Job, case: dict[str, Any], request_settings: Settings | None = None
    ) -> None:
        task = asyncio.create_task(self._execute(job, case, request_settings or self.settings))
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)

    async def _execute(
        self, job: Job, case: dict[str, Any], request_settings: Settings
    ) -> None:
        job.status = "running"
        job.message = "生成 A、评审并执行联合优化，期间会发起多次模型请求"
        try:
            service = SimpleImprovementService(request_settings)
            advisor = TargetedRepairAdvisor(ArkClient(request_settings))
            result = await optimize_case(case, service, advisor, job.run_dir)
            if result.get("error"):
                raise RuntimeError(result["error"])
            tos_meta = {"enabled": self.tos.enabled, "uploaded": False}
            job.message = "完成"
            if self.tos.enabled:
                try:
                    directories = result_run_directories(job, result, self.settings.runs_dir)
                    object_count = await self.tos.upload_directories(directories)
                    tos_meta = {
                        "enabled": True,
                        "uploaded": True,
                        "object_count": object_count,
                        "prefix": self.settings.tos_prefix,
                    }
                    job.message = "完成，结果已同步到 TOS"
                except Exception as exc:  # noqa: BLE001 - retain completed local results on TOS failure.
                    tos_meta = {
                        "enabled": True,
                        "uploaded": False,
                        "error": f"{type(exc).__name__}: {exc}"[:500],
                    }
                    job.message = "完成，但 TOS 上传失败，结果暂存本地"
            result["_tos"] = tos_meta
            write_json(job.run_dir / "result.json", result)
            if tos_meta.get("uploaded"):
                try:
                    await self.tos.upload_result(job.run_dir)
                    if self.settings.tos_delete_local_after_upload:
                        try:
                            for directory in directories:
                                if directory.exists() and directory.is_relative_to(
                                    self.settings.runs_dir.resolve()
                                ):
                                    shutil.rmtree(directory)
                            job.message = "完成，结果已同步到 TOS，本地缓存已清理"
                        except OSError:
                            job.message = "完成，结果已同步到 TOS；本地缓存清理失败"
                except Exception as exc:  # noqa: BLE001 - preserve the completed local result.
                    result["_tos"] = {
                        "enabled": True,
                        "uploaded": False,
                        "error": f"{type(exc).__name__}: {exc}"[:500],
                    }
                    write_json(job.run_dir / "result.json", result)
                    job.message = "完成，但 TOS 上传失败，结果暂存本地"
            job.result = result
            job.status = "done"
        except Exception as exc:  # noqa: BLE001 - expose a useful local job error.
            job.status = "failed"
            job.error = friendly_job_error(exc)
            job.message = "任务失败"
            write_json(
                job.run_dir / "error.json",
                {"error": job.error, "raw_error": f"{type(exc).__name__}: {exc}"},
            )
