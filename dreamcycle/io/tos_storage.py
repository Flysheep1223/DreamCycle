"""Private TOS persistence for completed DreamCycle runs and browser file access."""

from __future__ import annotations

import asyncio
import json
import mimetypes
from pathlib import Path, PurePosixPath

import tos

from dreamcycle.config import Settings


class TosStorage:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.enabled = settings.tos_enabled
        if self.enabled:
            self.client = tos.TosClientV2(
                settings.tos_access_key,
                settings.tos_secret_key,
                settings.tos_endpoint,
                settings.tos_region,
                security_token=settings.tos_session_token or None,
            )

    def key(self, relative_path: str) -> str:
        path = PurePosixPath(relative_path)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Invalid TOS relative path")
        return f"{self.settings.tos_prefix}/{path.as_posix()}"

    def run_relative_path(self, path: str | Path) -> str | None:
        parts = Path(path).parts
        markers = {"runs", "dreamcycle-runs"}
        indices = [index for index, part in enumerate(parts) if part in markers]
        if not indices:
            return None
        index = indices[-1]
        relative = PurePosixPath(*parts[index + 1 :])
        return relative.as_posix() if relative.parts else None

    def _upload_file(self, path: Path, relative: str) -> None:
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        with path.open("rb") as content:
            self.client.put_object(
                self.settings.tos_bucket,
                self.key(relative),
                content=content,
                content_type=content_type,
            )

    def _upload_directory(self, directory: Path) -> int:
        count = 0
        for path in sorted(directory.rglob("*")):
            if not path.is_file():
                continue
            relative = f"{directory.name}/{path.relative_to(directory).as_posix()}"
            self._upload_file(path, relative)
            count += 1
        return count

    async def upload_directories(self, directories: list[Path]) -> int:
        if not self.enabled:
            return 0

        def upload() -> int:
            return sum(self._upload_directory(directory) for directory in directories)

        return await asyncio.to_thread(upload)

    async def upload_result(self, job_dir: Path) -> None:
        if not self.enabled:
            return
        await asyncio.to_thread(
            self._upload_file, job_dir / "result.json", f"{job_dir.name}/result.json"
        )

    def read_job_result(self, job_id: str) -> dict | None:
        if not self.enabled:
            return None
        try:
            output = self.client.get_object(
                self.settings.tos_bucket, self.key(f"{job_id}/result.json")
            )
            return json.loads(output.read().decode("utf-8"))
        except tos.exceptions.TosServerError as exc:
            if exc.status_code == 404:
                return None
            raise

    def signed_url(self, relative_path: str, expires: int = 900) -> str:
        if not self.enabled:
            raise ValueError("TOS is not configured")
        output = self.client.pre_signed_url(
            tos.enum.HttpMethodType.Http_Method_Get,
            self.settings.tos_bucket,
            self.key(relative_path),
            expires=expires,
        )
        return output.signed_url
