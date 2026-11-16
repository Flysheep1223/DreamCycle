"""Measure repeatability of left/right-hand judgments on one fixed generated image."""

from __future__ import annotations

import asyncio
from collections import Counter

from EVA.ark import ArkClient
from EVA.config import get_settings
from EVA.io.storage import create_run_dir, write_json
from EVA.judge import VLMJudge
from EVA.schemas import CheckItem, RouteDecision, TaskMode

IMAGE = "EVA/runs/run-20261115T130037-d659a348/generated-00.png"
SOURCE_A = "EVA/runs/run-20261115T112951-3fa515a7/generated-00.png"
SOURCE_B = "EVA/runs/run-20261115T112951-e6f3d43a/generated-00.png"
PROMPT = (
    "组合两张输入图中的两位少女：图1银发绿眼少女与图2深色短发绿眼少女。"
    "银发少女站左侧，人物自身右手拿透明伞；深色短发少女站右侧，"
    "人物自身左手拿扳手（正面对观众时位于画面右侧），"
    "人物自身右手托一本红书（位于画面左侧），不得左右手互换。"
)
ROUTE = RouteDecision(
    modes=[TaskMode.REFERENCE_GENERATION],
    task_checklist=[
        CheckItem(
            id="left_hand_wrench",
            question="右侧深色短发少女是否用人物自身左手握扳手？正面朝向观众时，扳手应位于画面右侧。",
            expected="yes",
        ),
        CheckItem(
            id="right_hand_book",
            question="右侧深色短发少女是否用人物自身右手托红书？正面朝向观众时，红书应位于画面左侧。",
            expected="yes",
        ),
    ],
)


async def main(trials: int = 6) -> None:
    settings = get_settings()
    settings.validate(require_seedream=False)
    judge = VLMJudge(ArkClient(settings))
    run_id, run_dir = create_run_dir(settings.runs_dir, prefix="hand-probe")
    results = []
    protocol_failures = []
    for index in range(trials):
        try:
            result, raw = await judge.evaluate(
                prompt=PROMPT,
                route=ROUTE,
                input_images=[SOURCE_A, SOURCE_B],
                generated_image=IMAGE,
            )
        except Exception as exc:  # noqa: BLE001 - record malformed judge output as a protocol failure.
            failure = {
                "trial": index + 1,
                "error": f"{type(exc).__name__}: {exc}",
            }
            protocol_failures.append(failure)
            write_json(run_dir / f"trial-{index + 1:02d}-error.json", failure)
            print(f"trial {index + 1}: protocol failure: {type(exc).__name__}", flush=True)
            continue
        scores = {check.id: check.score for check in result.checks}
        reasons = {check.id: check.reason for check in result.checks}
        left_error = scores.get("left_hand_wrench", 0) <= 0.5
        right_error = scores.get("right_hand_book", 0) <= 0.5
        results.append(
            {
                "trial": index + 1,
                "scores": scores,
                "reasons": reasons,
                "left_hand_error": left_error,
                "right_hand_error": right_error,
                "any_hand_error": left_error or right_error,
            }
        )
        write_json(run_dir / f"trial-{index + 1:02d}.json", raw)
        print(
            f"trial {index + 1}: left={scores.get('left_hand_wrench')} "
            f"right={scores.get('right_hand_book')} any_error={left_error or right_error}",
            flush=True,
        )
    error_counts = Counter(
        key
        for result in results
        for key in ["left_hand_error", "right_hand_error", "any_hand_error"]
        if result[key]
    )
    summary = {
        "run_id": run_id,
        "trials": trials,
        "image": IMAGE,
        "reference_interpretation": (
            "直接核对生成图：右侧人物自身左手持扳手、自身右手托红书，按此作为本轮正确的参照解释。"
        ),
        "error_definition": "对应检查项得分<=0.5视为该机评误判；任何一只手误判即any_hand_error。",
        "error_counts": dict(error_counts),
        "error_rates": {
            key: error_counts.get(key, 0) / max(len(results), 1)
            for key in ["left_hand_error", "right_hand_error", "any_hand_error"]
        },
        "valid_trials": len(results),
        "protocol_failures": protocol_failures,
        "results": results,
    }
    write_json(run_dir / "summary.json", summary)
    print(f"summary: {summary['error_rates']}")


if __name__ == "__main__":
    asyncio.run(main())
