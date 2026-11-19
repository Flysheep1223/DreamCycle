"""Image conversion helpers shared by generation and VLM judging."""

from __future__ import annotations

import base64
import io
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, ImageOps


def is_url(value: str) -> bool:
    return urlparse(value).scheme in {"http", "https"}


def image_to_data_uri(source: str | Path, max_side: int = 1280, quality: int = 88) -> str:
    """Return an HTTP URL unchanged, or convert a local image to a bounded JPEG data URI."""
    source = str(source)
    if is_url(source):
        return source
    path = Path(source).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Input image does not exist: {path}")
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def image_part(source: str | Path, detail: str = "high", max_side: int = 1280) -> dict:
    return {
        "type": "image_url",
        "image_url": {
            "url": image_to_data_uri(source, max_side=max_side),
            "detail": detail,
        },
    }


def text_part(text: str) -> dict:
    return {"type": "text", "text": text}
