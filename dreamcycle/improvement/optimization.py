"""Production A/B optimization and joint-repair orchestration for the HTML client."""

from __future__ import annotations

import json
from pathlib import Path

from dreamcycle.dream_indicators.selection import compare_to_incumbent
from dreamcycle.improvement.repair import (
    TargetedRepairAdvisor,
    all_requirements_pass,
    best_partial_candidate,
    has_repair_potential,
    strict_success,
)
from dreamcycle.improvement.service import SimpleImprovementService
from dreamcycle.schemas import EvaluationResult, RouteDecision

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAX_REPAIRS = 5


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluation(path: str) -> EvaluationResult:
    return EvaluationResult.model_validate(read_json(Path(path) / "score-00.json"))


async def optimize_case(
    case: dict,
    service: SimpleImprovementService,
    repair_advisor: TargetedRepairAdvisor,
    parent: Path,
) -> dict:
    case_name = case["case"]
    try:
        image_path = str(PROJECT_ROOT / case["image"]) if case.get("image") else None
        input_images = [str(PROJECT_ROOT / path) for path in case.get("input_images", [])]
        base_seed = case["seed"]
        first = await service.improve(
            prompt=case["prompt"],
            input_images=input_images,
            target_texts=case["target_texts"],
            generated_image=image_path,
            generation_size=case["size"],
            generation_seed=base_seed,
            case=case_name,
            stop_if_a_passes=True,
        )
        original_a = evaluation(first["a"]["output_dir"])
        if first.get("skipped_b"):
            return {
                "case": case_name,
                "title": case["title"],
                "original": {
                    "prompt": case["prompt"],
                    "image": original_a.image.path,
                    "metrics": original_a.metrics,
                    "output_dir": first["a"]["output_dir"],
                },
                "first": first,
                "repairs": [],
                "attempts": [],
                "accepted": True,
                "final_status": "accepted",
                "final_source": "A",
                "final_image": original_a.image.path,
                "final_metrics": original_a.metrics,
                "final_comparison": first["comparison"],
            }
        current = evaluation(first["b"]["output_dir"])
        route = RouteDecision.model_validate(
            read_json(Path(first["a"]["output_dir"]) / "route.json")
        )
        accepted = strict_success(original_a.metrics, current.metrics)
        first["strict_success"] = accepted
        first["all_requirements_pass"] = all_requirements_pass(current.metrics)
        attempts = [
            {
                "name": "B1",
                "prompt": first["revised_prompt"],
                "prompt_source": "feedback_rewrite",
                "image": current.image.path,
                "metrics": current.metrics,
                "output_dir": first["b"]["output_dir"],
                "comparison_to_original_a": first["comparison"],
                "accepted": accepted,
            }
        ]
        final_evaluation = current
        final_comparison = first["comparison"]
        final_source = "B1"
        print(
            f"{case_name} first_b accepted={accepted} task={current.metrics.get('task_score')}",
            flush=True,
        )

        base = current if has_repair_potential(original_a.metrics, current.metrics) else original_a
        base_prompt = first["revised_prompt"] if base is current else case["prompt"]
        repairs = []
        for repair_index in range(1, MAX_REPAIRS + 1):
            if accepted:
                break
            advice, advice_raw = await repair_advisor.review(
                original_prompt=case["prompt"],
                base_prompt=base_prompt,
                route=route,
                original_a=original_a,
                base=base,
                original_input_images=input_images,
            )
            generation_dir = parent / f"{case_name}-repair-{repair_index}"
            generation_dir.mkdir(parents=True, exist_ok=True)
            images = await service.pipeline.generator.generate(
                prompt=advice.revised_generation_prompt,
                input_images=[base.image.path],
                run_dir=generation_dir,
                size=case["size"],
                seed=base_seed + repair_index * 100,
                guidance_scale=None,
            )
            evaluated = await service.pipeline.run(
                prompt=case["prompt"],
                input_images=input_images,
                target_texts=case["target_texts"],
                generated_image=images[0].path,
                evaluation_route=route,
                include_advice=False,
            )
            current = evaluated.evaluations[0]
            comparison = compare_to_incumbent(original_a.metrics, current.metrics)
            accepted = strict_success(original_a.metrics, current.metrics)
            repair = {
                "name": f"B{repair_index + 1}",
                "target_check_ids": advice_raw["target_check_ids"],
                "base_image": base.image.path,
                "base_prompt": base_prompt,
                "repair_prompt": advice.revised_generation_prompt,
                "suggestions": advice.generation_prompt_suggestions,
                "assessment": advice.overall_assessment,
                "image": current.image.path,
                "metrics": current.metrics,
                "output_dir": evaluated.output_dir,
                "generation_dir": str(generation_dir),
                "comparison_to_original_a": comparison,
                "accepted": accepted,
            }
            repairs.append(repair)
            attempts.append(repair)
            print(
                f"{case_name} repair_{repair_index} targets={advice_raw['target_check_ids']} "
                f"accepted={accepted} task={current.metrics.get('task_score')}",
                flush=True,
            )
            if accepted:
                final_evaluation = current
                final_comparison = comparison
                final_source = repair["name"]
                break
            if has_repair_potential(original_a.metrics, current.metrics):
                base = current
                base_prompt = advice.revised_generation_prompt

        final_status = "accepted"
        if not accepted:
            partial = best_partial_candidate(original_a.metrics, attempts)
            if partial is not None:
                final_evaluation = evaluation(partial["output_dir"])
                final_source = partial["name"]
                final_comparison = partial["comparison_to_original_a"]
                final_status = "partial_improvement"
            else:
                final_evaluation = original_a
                final_source = "original_a_retained"
                final_status = "original_a_retained"
                final_comparison = {
                    "accepted": False,
                    "improved": [],
                    "degraded": [],
                    "comparisons": [],
                }
        return {
            "case": case_name,
            "title": case["title"],
            "original": {
                "prompt": case["prompt"],
                "image": original_a.image.path,
                "metrics": original_a.metrics,
                "output_dir": first["a"]["output_dir"],
            },
            "first": first,
            "repairs": repairs,
            "attempts": attempts,
            "accepted": accepted,
            "final_status": final_status,
            "final_source": final_source,
            "final_image": final_evaluation.image.path,
            "final_metrics": final_evaluation.metrics,
            "final_comparison": final_comparison,
        }
    except Exception as exc:  # noqa: BLE001 - preserve independent case results.
        return {"case": case_name, "title": case["title"], "error": f"{type(exc).__name__}: {exc}"}
