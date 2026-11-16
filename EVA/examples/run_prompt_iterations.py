"""Iterate independent prompt revisions to A/B/C/D/E with one fixed evaluation checklist."""

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

ROOT = Path(__file__).resolve().parents[1]
NEXT_STAGE = {"A": "B", "B": "C", "C": "D", "D": "E"}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


async def iterate_case(
    comparison: dict, advisor: PromptAdvisor, pipeline: EvaluationPipeline, root: Path
) -> dict:
    original = comparison["original"]
    case = original["case"]
    route = RouteDecision.model_validate(read_json(Path(original["output_dir"]) / "route.json"))
    a_result = await pipeline.run(
        prompt=original["prompt"],
        input_images=original.get("input_images", []),
        target_texts=original.get("target_texts", []),
        evaluation_route=route,
        include_advice=False,
    )
    a_evaluation = a_result.evaluations[0]
    stages = {
        "A": {
            "prompt": original["prompt"],
            "image": a_evaluation.image.path,
            "metrics": a_evaluation.metrics,
            "output_dir": a_result.output_dir,
        }
    }
    errors = []
    for previous_name, next_name in NEXT_STAGE.items():
        previous = stages[previous_name]
        try:
            evaluation = EvaluationResult.model_validate(
                read_json(Path(previous["output_dir"]) / "score-00.json")
            )
            advice, advice_raw = await advisor.review(
                prompt=previous["prompt"],
                original_prompt=original["prompt"],
                route=route,
                result=evaluation,
                input_images=original.get("input_images", []),
            )
            result = await pipeline.run(
                prompt=advice.revised_generation_prompt,
                input_images=original.get("input_images", []),
                target_texts=original.get("target_texts", []),
                evaluation_route=route,
                include_advice=False,
            )
            evaluation = result.evaluations[0]
            stages[next_name] = {
                "prompt": advice.revised_generation_prompt,
                "image": evaluation.image.path,
                "metrics": evaluation.metrics,
                "output_dir": result.output_dir,
                "advisor_raw": advice_raw,
            }
            write_json(root / f"{case}-{next_name}.json", stages[next_name])
        except Exception as exc:  # noqa: BLE001 - preserve completed stages and other cases.
            errors.append({"stage": next_name, "error": f"{type(exc).__name__}: {exc}"})
            break
    return {
        "case": case,
        "route": route.model_dump(mode="json"),
        "stages": stages,
        "errors": errors,
    }


async def main() -> None:
    settings = get_settings()
    settings.validate()
    ab_dir = max((ROOT / "runs").glob("prompt-ab-showcase-*"), key=lambda path: path.name)
    fixed_summary = read_json(ab_dir / "fixed_summary.json")
    run_id, run_dir = create_run_dir(settings.runs_dir, prefix="prompt-iterations")
    advisor = PromptAdvisor(ArkClient(settings))
    pipeline = EvaluationPipeline(settings)
    comparisons = await asyncio.gather(
        *(
            iterate_case(comparison, advisor, pipeline, run_dir)
            for comparison in fixed_summary["comparisons"]
        )
    )
    summary = {
        "run_id": run_id,
        "output_dir": str(run_dir),
        "note": (
            "A-E全部重新生成，均使用A原始Prompt的同一套检查清单；B-E采用原始需求锚定、"
            "有限局部改写和字符预算，不累计新增约束；VLM temperature=0，生图未固定seed。"
        ),
        "revision_policy": "source_anchored_equivalent_revision_v3",
        "cases": comparisons,
    }
    write_json(run_dir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
