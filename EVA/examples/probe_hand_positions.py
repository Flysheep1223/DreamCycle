"""Repeat the coordinate-based hand evaluation on the same task-4 image."""

from __future__ import annotations

import asyncio

from EVA.ark import ArkClient
from EVA.config import get_settings
from EVA.io.storage import create_run_dir, write_json
from EVA.spatial import SpatialHandJudge

IMAGE = "EVA/runs/run-20261115T130037-d659a348/generated-00.png"


async def main(trials: int = 4) -> None:
    settings = get_settings()
    settings.validate(require_seedream=False)
    judge = SpatialHandJudge(ArkClient(settings))
    run_id, run_dir = create_run_dir(settings.runs_dir, prefix="hand-position-probe")
    results = []
    failures = []
    for index in range(trials):
        try:
            result, raw = await judge.evaluate(IMAGE)
        except Exception as exc:  # noqa: BLE001 - keep independent trials isolated.
            failures.append({"trial": index + 1, "error": str(exc)})
            continue
        item = result.model_dump()
        item["trial"] = index + 1
        item["any_error"] = not (result.left_hand_wrench_correct and result.right_hand_book_correct)
        results.append(item)
        write_json(run_dir / f"trial-{index + 1:02d}.json", {"raw": raw, "computed": item})
        print(item, flush=True)
    summary = {
        "run_id": run_id,
        "trials": trials,
        "valid_trials": len(results),
        "errors": sum(item["any_error"] for item in results),
        "error_rate": sum(item["any_error"] for item in results) / max(len(results), 1),
        "protocol_failures": failures,
        "results": results,
    }
    write_json(run_dir / "summary.json", summary)
    print(
        {
            key: value
            for key, value in summary.items()
            if key not in {"results", "protocol_failures"}
        }
    )


if __name__ == "__main__":
    asyncio.run(main())
