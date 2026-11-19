"""Migrate existing run directories to private TOS, deleting each verified local copy."""

from __future__ import annotations

import argparse
import asyncio
import shutil
from pathlib import Path

from dreamcycle.config import get_settings
from dreamcycle.io.tos_storage import TosStorage


def directory_size(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


async def migrate(*, confirmed: bool) -> None:
    settings = get_settings()
    storage = TosStorage(settings)
    if not storage.enabled:
        raise RuntimeError("TOS is not fully configured")
    directories = sorted(path for path in settings.runs_dir.iterdir() if path.is_dir())
    total_bytes = sum(directory_size(path) for path in directories)
    print(f"directories={len(directories)} size_mb={total_bytes / 1024 / 1024:.1f}")
    if not confirmed:
        print("Dry run only. Re-run with --yes to upload and delete verified local copies.")
        return
    migrated = 0
    objects = 0
    for directory in directories:
        try:
            count = await storage.upload_directories([directory])
        except Exception as exc:
            print(f"Stopped at {directory.name}: {type(exc).__name__}: {str(exc)[:500]}")
            print(f"Directories migrated before stop: {migrated}")
            raise
        shutil.rmtree(directory)
        migrated += 1
        objects += count
        print(f"Migrated {directory.name}: {count} objects", flush=True)
    print(f"Migration complete: directories={migrated}, objects={objects}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--yes", action="store_true", help="Upload and delete verified local copies")
    args = parser.parse_args()
    asyncio.run(migrate(confirmed=args.yes))


if __name__ == "__main__":
    main()
