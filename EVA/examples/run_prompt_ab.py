"""Generate revised prompts independently and compare them with retained original outputs."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from EVA.ark import ArkClient
from EVA.config import get_settings
from EVA.io.storage import create_run_dir, write_json
from EVA.pipeline import EvaluationPipeline
from EVA.reviewer import PromptAdvisor
from EVA.schemas import EvaluationResult, RouteDecision

SUMMARY_PATH = "EVA/runs/ood-showcase-20261115T145746-9fa1d346/summary.json"
SNOW_SCORE_PATH = "EVA/runs/run-20261115T150838-3c994afe/score-00.json"
SNOW_RUN_DIR = "EVA/runs/run-20261115T150838-3c994afe"


def _original_cases() -> list[dict]:
    summary = json.loads(Path(SUMMARY_PATH).read_text(encoding="utf-8"))
    cases = [*summary["t2i"], *summary["dependent"]]
    snow_score = json.loads(Path(SNOW_SCORE_PATH).read_text(encoding="utf-8"))
    for case in cases:
        if case["case"] == "ood_style_snow_egret":
            case["metrics"] = snow_score["metrics"]
            case["advice"] = snow_score.get("advice")
            case["output_dir"] = SNOW_RUN_DIR
    return cases


def _read_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


async def _revised_case_impl(
    original: dict,
    advisor: PromptAdvisor,
    pipeline: EvaluationPipeline,
) -> dict:
    route_data = await asyncio.to_thread(_read_json, original["output_dir"] + "/route.json")
    score_data = await asyncio.to_thread(_read_json, original["output_dir"] + "/score-00.json")
    route = RouteDecision.model_validate(route_data)
    evaluation = EvaluationResult.model_validate(score_data)
    advice, advice_raw = await advisor.review(
        prompt=original["prompt"],
        route=route,
        result=evaluation,
        input_images=original.get("input_images", []),
    )
    revised_prompt = advice.revised_generation_prompt
    revised_result = await pipeline.run(
        prompt=revised_prompt,
        input_images=original.get("input_images", []),
        target_texts=original.get("target_texts", []),
    )
    return {
        "case": original["case"],
        "original": original,
        "revised_prompt": revised_prompt,
        "advisor_raw": advice_raw,
        "revised": revised_result.model_dump(mode="json"),
    }


async def _revised_case(
    original: dict, advisor: PromptAdvisor, pipeline: EvaluationPipeline
) -> dict:
    try:
        return await _revised_case_impl(original, advisor, pipeline)
    except Exception as exc:  # noqa: BLE001 - keep independent A/B cases running.
        return {
            "case": original["case"],
            "original": original,
            "error": f"{type(exc).__name__}: {exc}",
        }


async def main() -> None:
    settings = get_settings()
    settings.validate()
    showcase_id, showcase_dir = create_run_dir(settings.runs_dir, prefix="prompt-ab-showcase")
    advisor = PromptAdvisor(ArkClient(settings))
    pipeline = EvaluationPipeline(settings)
    originals = _original_cases()
    print(f"Prompt A/B directory: {showcase_dir}", flush=True)
    comparisons = await asyncio.gather(
        *(_revised_case(original, advisor, pipeline) for original in originals)
    )
    summary = {
        "showcase_id": showcase_id,
        "showcase_dir": str(showcase_dir),
        "note": "B组使用独立Advisor改写Prompt重新生成；A组保留原结果。当前Seedream版本未固定seed，差异包含随机波动。",
        "comparisons": comparisons,
    }
    write_json(showcase_dir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
