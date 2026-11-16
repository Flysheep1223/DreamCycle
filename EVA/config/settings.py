"""Environment based configuration. Secrets are never included in repr output."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=False)


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    ark_api_key: str = field(repr=False, default="")
    ark_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    vlm_model: str = ""
    seedream_model: str = ""
    seedream_size: str = "2K"
    seedream_watermark: bool = False
    workers: int = 4
    advisor_enabled: bool = True
    vlm_temperature: float = 0.0
    vlm_max_tokens: int = 4096
    download_timeout_seconds: float = 120.0
    runs_dir: Path = PROJECT_ROOT / "EVA" / "runs"

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            ark_api_key=os.getenv("ARK_API_KEY", ""),
            ark_base_url=os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
            vlm_model=os.getenv("VLM_MODEL", ""),
            seedream_model=os.getenv("SEEDREAM_MODEL", ""),
            seedream_size=os.getenv("SEEDREAM_SIZE", "2K"),
            seedream_watermark=_bool("SEEDREAM_WATERMARK", False),
            workers=max(1, int(os.getenv("DREAMER_WORKERS", "4"))),
            advisor_enabled=_bool("ADVISOR_ENABLED", True),
            vlm_temperature=float(os.getenv("VLM_TEMPERATURE", "0")),
            vlm_max_tokens=int(os.getenv("VLM_MAX_TOKENS", "4096")),
            download_timeout_seconds=float(os.getenv("DOWNLOAD_TIMEOUT_SECONDS", "120")),
            runs_dir=Path(os.getenv("EVA_RUNS_DIR", str(PROJECT_ROOT / "EVA" / "runs"))),
        )

    def validate(self, require_seedream: bool = True) -> None:
        missing = []
        if not self.ark_api_key:
            missing.append("ARK_API_KEY")
        if not self.vlm_model:
            missing.append("VLM_MODEL")
        if require_seedream and not self.seedream_model:
            missing.append("SEEDREAM_MODEL")
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    def public_dict(self) -> dict[str, object]:
        """Return non-secret settings suitable for logs and the /health endpoint."""
        return {
            "ark_base_url": self.ark_base_url,
            "vlm_model": self.vlm_model,
            "seedream_model": self.seedream_model,
            "seedream_size": self.seedream_size,
            "seedream_watermark": self.seedream_watermark,
            "workers": self.workers,
            "advisor_enabled": self.advisor_enabled,
            "vlm_temperature": self.vlm_temperature,
            "runs_dir": str(self.runs_dir),
            "ark_api_key_configured": bool(self.ark_api_key),
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()
