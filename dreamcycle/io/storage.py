"""Run directories, bounded downloads and JSON persistence."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import httpx
from PIL import Image

MAX_DOWNLOAD_BYTES = 40 * 1024 * 1024


def create_run_dir(root: Path, prefix: str = "run") -> tuple[str, Path]:
    run_id = f"{prefix}-{datetime.now(UTC).strftime('%Y%m%dT%H%M%S')}-{uuid4().hex[:8]}"
    directory = root / run_id
    directory.mkdir(parents=True, exist_ok=False)
    return run_id, directory


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


async def download_image(url: str, destination: Path, timeout: float) -> Path:
    """Download an Ark result URL and re-save as PNG so downstream readers are consistent."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        if len(response.content) > MAX_DOWNLOAD_BYTES:
            raise ValueError("Generated image exceeds the 40 MB download limit")
        destination.write_bytes(response.content)
    with Image.open(destination) as image:
        image.load()
        if image.format not in {"PNG", "JPEG", "WEBP"}:
            raise ValueError(f"Unsupported generated image format: {image.format}")
        image.convert("RGB").save(destination, format="PNG")
    return destination
