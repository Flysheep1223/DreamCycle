"""Run guarded A-E optimization with fixed generation parameters and best checkpoints."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from EVA.ark import ArkClient
from EVA.config import get_settings
from EVA.io.storage import create_run_dir, write_json
from EVA.pipeline import EvaluationPipeline
from EVA.reviewer import PromptAdvisor
from EVA.schemas import EvaluationResult, RouteDecision
from EVA.scoring.selection import select_pareto_candidate

ROOT = Path(__file__).resolve().parents[1]
STAGES = ["A", "B", "C", "D", "E"]
NEXT_STAGE = {"A": "B", "B": "C", "C": "D", "D": "E"}
CANDIDATES_PER_STAGE = 4
GUIDANCE_SCALE = None  # This Seedream endpoint rejects explicit guidance_scale.
CASE_GENERATION = {
    "ood_macro_watch": {"size": "2496x1664", "base_seed": 41000},
    "ood_gongbi_blueprint": {"size": "2816x1584", "base_seed": 42000},
    "ood_greenhouse_dashboard": {"size": "2816x1584", "base_seed": 43000},
    "ood_woodcut_arctic": {"size": "2496x1664", "base_seed": 44000},
    "ood_style_snow_egret": {"size": "1776x2368", "base_seed": 45000},
    "ood_edit_watch_background": {"size": "2496x1664", "base_seed": 46000},
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def generation_config(case: str, slot: int, stage: str) -> dict[str, Any]:
    config = CASE_GENERATION[case]
    # A/B share a control block; later stages use new deterministic blocks to avoid repeats.
    seed_block = max(0, STAGES.index(stage) - 1)
    return {
        "size": config["size"],
        "seed": config["base_seed"] + seed_block * CANDIDATES_PER_STAGE + slot,
        "guidance_scale": GUIDANCE_SCALE,
        "output_format": "png",
        "response_format": "url",
        "watermark": False,
        "candidate_slot": slot,
    }


def checkpoint_fields(stage: dict) -> dict:
    return {
        key: stage[key]
        for key in ("prompt", "image", "metrics", "output_dir", "generation", "source_stage")
    }


def result_fields(result, prompt: str, generation: dict, stage: str) -> dict:
    evaluation = result.evaluations[0]
    return {
        "prompt": prompt,
        "image": evaluation.image.path,
        "metrics": evaluation.metrics,
        "output_dir": result.output_dir,
        "generation": generation,
        "source_stage": stage,
    }


async def generate_candidate(
    pipeline: EvaluationPipeline,
    *,
    prompt: str,
    original: dict,
    route: RouteDecision,
    generation: dict,
    prompt_source: str,
):
    try:
        result = await pipeline.run(
            prompt=prompt,
            input_images=original.get("input_images", []),
            target_texts=original.get("target_texts", []),
            evaluation_route=route,
            include_advice=False,
            generation_size=generation["size"],
            generation_seed=generation["seed"],
            generation_guidance_scale=generation["guidance_scale"],
        )
        return {
            "result": result,
            "generation": generation,
            "prompt": prompt,
            "prompt_source": prompt_source,
        }
    except Exception as exc:  # noqa: BLE001 - one rejected image must not discard other candidates.
        return {
            "error": f"{type(exc).__name__}: {exc}",
            "generation": generation,
            "prompt": prompt,
            "prompt_source": prompt_source,
        }


async def iterate_case(
    comparison: dict, advisor: PromptAdvisor, pipeline: EvaluationPipeline, root: Path
) -> dict:
    original = comparison["original"]
    case = original["case"]
    route = RouteDecision.model_validate(read_json(Path(original["output_dir"]) / "route.json"))
    stages = {}
    for stage_name in ("A", "B"):
        checkpoint_path = root / f"{case}-{stage_name}.json"
        if checkpoint_path.is_file():
            stages[stage_name] = read_json(checkpoint_path)
    if "A" not in stages:
        a_generation = generation_config(case, 0, "A")
        a_result = await pipeline.run(
            prompt=original["prompt"],
            input_images=original.get("input_images", []),
            target_texts=original.get("target_texts", []),
            evaluation_route=route,
            include_advice=False,
            generation_size=a_generation["size"],
            generation_seed=a_generation["seed"],
            generation_guidance_scale=a_generation["guidance_scale"],
        )
        stages["A"] = {
            **result_fields(a_result, original["prompt"], a_generation, "A"),
            "accepted": None,
            "candidates": [],
            "generation_errors": [],
        }
        write_json(root / f"{case}-A.json", stages["A"])
    best = stages.get("B", stages["A"])

    for next_name in NEXT_STAGE.values():
        if next_name in stages:
            continue
        try:
            evaluation = EvaluationResult.model_validate(
                read_json(Path(best["output_dir"]) / "score-00.json")
            )
            advice, advice_raw = await advisor.review(
                prompt=best["prompt"],
                original_prompt=original["prompt"],
                route=route,
                result=evaluation,
                input_images=original.get("input_images", []),
            )
            revised_prompt = advice.revised_generation_prompt
            candidate_specs = []
            for slot in range(CANDIDATES_PER_STAGE):
                prompt_source = "incumbent" if slot < CANDIDATES_PER_STAGE // 2 else "revised"
                candidate_specs.append(
                    {
                        "generation": generation_config(case, slot, next_name),
                        "prompt": best["prompt"]
                        if prompt_source == "incumbent"
                        else revised_prompt,
                        "prompt_source": prompt_source,
                    }
                )
            outcomes = await asyncio.gather(
                *(
                    generate_candidate(
                        pipeline,
                        prompt=spec["prompt"],
                        original=original,
                        route=route,
                        generation=spec["generation"],
                        prompt_source=spec["prompt_source"],
                    )
                    for spec in candidate_specs
                )
            )
            successful = []
            generation_errors = []
            for outcome in outcomes:
                if "error" in outcome:
                    generation_errors.append(
                        {
                            "generation": outcome["generation"],
                            "prompt_source": outcome["prompt_source"],
                            "error": outcome["error"],
                        }
                    )
                    continue
                fields = result_fields(
                    outcome["result"], outcome["prompt"], outcome["generation"], next_name
                )
                fields["prompt_source"] = outcome["prompt_source"]
                successful.append(fields)
            selected, decisions = select_pareto_candidate(best["metrics"], successful)
            candidate_records = []
            for index, candidate in enumerate(successful):
                candidate_records.append(
                    {
                        **candidate,
                        "selection": decisions[index],
                        "selected": index == selected,
                    }
                )
            if selected is None:
                best = {
                    **checkpoint_fields(best),
                    "accepted": False,
                    "source_stage": best["source_stage"],
                    "candidate_prompt": revised_prompt,
                    "advisor_raw": advice_raw,
                    "candidates": candidate_records,
                    "generation_errors": generation_errors,
                    "plateau_reason": "没有候选满足帕累托改善，保留历史最佳检查点。",
                }
            else:
                chosen = successful[selected]
                best = {
                    **checkpoint_fields(chosen),
                    "accepted": True,
                    "accepted_prompt_source": chosen["prompt_source"],
                    "candidate_prompt": revised_prompt,
                    "advisor_raw": advice_raw,
                    "candidates": candidate_records,
                    "generation_errors": generation_errors,
                    "selection": decisions[selected],
                }
        except Exception as exc:  # noqa: BLE001 - preserve the best checkpoint and other cases.
            best = {
                **checkpoint_fields(best),
                "accepted": False,
                "candidate_prompt": None,
                "candidates": [],
                "generation_errors": [],
                "stage_error": f"{type(exc).__name__}: {exc}",
                "plateau_reason": "本轮改写或候选流程异常，保留历史最佳检查点。",
            }
        stages[next_name] = best
        write_json(root / f"{case}-{next_name}.json", best)

    return {
        "case": case,
        "route": route.model_dump(mode="json"),
        "fixed_generation": {
            "size": CASE_GENERATION[case]["size"],
            "guidance_scale": GUIDANCE_SCALE,
            "seed_schedule": {
                stage_name: [
                    generation_config(case, slot, stage_name)["seed"]
                    for slot in range(CANDIDATES_PER_STAGE if stage_name != "A" else 1)
                ]
                for stage_name in STAGES
            },
            "output_format": "png",
            "response_format": "url",
            "watermark": False,
        },
        "stages": stages,
        "errors": [stage["stage_error"] for stage in stages.values() if "stage_error" in stage],
    }


async def main() -> None:
    settings = get_settings()
    settings.validate()
    ab_dir = max((ROOT / "runs").glob("prompt-ab-showcase-*"), key=lambda path: path.name)
    fixed_summary = read_json(ab_dir / "fixed_summary.json")
    resume_dir = os.getenv("EVA_OPTIMIZATION_RESUME_DIR")
    if resume_dir:
        run_dir = Path(resume_dir).expanduser().resolve()
        run_id = run_dir.name
    else:
        run_id, run_dir = create_run_dir(settings.runs_dir, prefix="prompt-optimization")
    advisor = PromptAdvisor(ArkClient(settings))
    pipeline = EvaluationPipeline(settings)
    cases = await asyncio.gather(
        *(
            iterate_case(comparison, advisor, pipeline, run_dir)
            for comparison in fixed_summary["comparisons"]
        )
    )
    summary = {
        "run_id": run_id,
        "output_dir": str(run_dir),
        "resumed_from": str(run_dir) if resume_dir else None,
        "note": (
            "A为固定seed的单样本起点；B保留首轮4个改写候选；C-E使用互不重复的固定seed块，"
            "每轮2个候选继承最佳Prompt、2个使用改写Prompt。仅接受无受保护指标下降且至少一项改善的候选，"
            "否则继承历史最佳检查点。"
        ),
        "revision_policy": "best_checkpoint_guarded_revision_v4",
        "selection_rule": (
            "帕累托验收：动态VQA、保持度、PQ、布局、全项通过率、最低检查项、OCR、"
            "编辑SC/PQ和参考CP/PF均不得下降；至少一项改善。只用字典序选胜，不计算总分。"
        ),
        "candidates_per_stage": CANDIDATES_PER_STAGE,
        "unsupported_generation_parameters": {
            "guidance_scale": "端点实测返回 InvalidParameter，因此所有请求均不传此参数。"
        },
        "vlm": {
            "model": settings.vlm_model,
            "temperature": settings.vlm_temperature,
            "thinking": "disabled",
            "max_tokens": settings.vlm_max_tokens,
        },
        "cases": cases,
    }
    write_json(run_dir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
