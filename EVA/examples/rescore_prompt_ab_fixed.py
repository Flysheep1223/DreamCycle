"""Re-score A/B images using exactly the original prompt's checklist for both sides."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from EVA.config import get_settings
from EVA.pipeline import EvaluationPipeline
from EVA.schemas import RouteDecision

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


async def rescore(comparison: dict, pipeline: EvaluationPipeline) -> dict:
    original = comparison["original"]
    if "error" in comparison:
        return comparison
    route = RouteDecision.model_validate(read_json(Path(original["output_dir"]) / "route.json"))
    kwargs = {
        "prompt": original["prompt"],
        "input_images": original.get("input_images", []),
        "target_texts": original.get("target_texts", []),
        "evaluation_route": route,
        "include_advice": False,
    }
    a_result, b_result = await asyncio.gather(
        pipeline.run(generated_image=original["image"], **kwargs),
        pipeline.run(
            generated_image=comparison["revised"]["evaluations"][0]["image"]["path"],
            **kwargs,
        ),
    )
    return {
        **comparison,
        "fixed_original_metrics": a_result.evaluations[0].metrics,
        "fixed_revised_metrics": b_result.evaluations[0].metrics,
        "fixed_route": route.model_dump(mode="json"),
        "fixed_original_run": a_result.output_dir,
        "fixed_revised_run": b_result.output_dir,
    }


async def main() -> None:
    directory = max((ROOT / "runs").glob("prompt-ab-showcase-*"), key=lambda path: path.name)
    summary = read_json(directory / "summary.json")
    pipeline = EvaluationPipeline(get_settings())
    comparisons = await asyncio.gather(
        *(rescore(comparison, pipeline) for comparison in summary["comparisons"])
    )
    output = {
        "showcase_id": summary["showcase_id"],
        "showcase_dir": summary["showcase_dir"],
        "note": "A、B两组图片均使用A原始Prompt生成的同一套检查清单重新评分，避免动态VQA评估标准变化。",
        "comparisons": comparisons,
    }
    path = directory / "fixed_summary.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    asyncio.run(main())
