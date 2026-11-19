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
    cors_origins: str = ""
    advisor_enabled: bool = True
    vlm_temperature: float = 0.0
    vlm_max_tokens: int = 4096
    judge_repeats: int = 10
    download_timeout_seconds: float = 120.0
    runs_dir: Path = PROJECT_ROOT / "dreamcycle" / "runs"
    tos_access_key: str = field(repr=False, default="")
    tos_secret_key: str = field(repr=False, default="")
    tos_session_token: str = field(repr=False, default="")
    tos_endpoint: str = ""
    tos_region: str = ""
    tos_bucket: str = ""
    tos_prefix: str = "dreamcycle/runs"
    tos_delete_local_after_upload: bool = True

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
            cors_origins=os.getenv("DREAMCYCLE_CORS_ORIGINS", os.getenv("EVA_CORS_ORIGINS", "")),
            advisor_enabled=_bool("ADVISOR_ENABLED", True),
            vlm_temperature=float(os.getenv("VLM_TEMPERATURE", "0")),
            vlm_max_tokens=int(os.getenv("VLM_MAX_TOKENS", "4096")),
            judge_repeats=max(1, int(os.getenv("JUDGE_REPEATS", "10"))),
            download_timeout_seconds=float(os.getenv("DOWNLOAD_TIMEOUT_SECONDS", "120")),
            runs_dir=Path(
                os.getenv(
                    "DREAMCYCLE_RUNS_DIR",
                    os.getenv("EVA_RUNS_DIR", str(PROJECT_ROOT / "dreamcycle" / "runs")),
                )
            ),
            tos_access_key=os.getenv("TOS_ACCESS_KEY", ""),
            tos_secret_key=os.getenv("TOS_SECRET_KEY", ""),
            tos_session_token=os.getenv("TOS_SESSION_TOKEN", ""),
            tos_endpoint=os.getenv("TOS_ENDPOINT", ""),
            tos_region=os.getenv("TOS_REGION", ""),
            tos_bucket=os.getenv("TOS_BUCKET", ""),
            tos_prefix=os.getenv("TOS_PREFIX", "dreamcycle/runs").strip("/"),
            tos_delete_local_after_upload=_bool("TOS_DELETE_LOCAL_AFTER_UPLOAD", True),
        )

    @property
    def tos_enabled(self) -> bool:
        return all(
            (
                self.tos_access_key,
                self.tos_secret_key,
                self.tos_endpoint,
                self.tos_region,
                self.tos_bucket,
                self.tos_prefix,
            )
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
            "judge_repeats": self.judge_repeats,
            "runs_dir": str(self.runs_dir),
            "ark_api_key_configured": bool(self.ark_api_key),
            "tos_enabled": self.tos_enabled,
            "tos_prefix": self.tos_prefix,
            "tos_delete_local_after_upload": self.tos_delete_local_after_upload,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()
