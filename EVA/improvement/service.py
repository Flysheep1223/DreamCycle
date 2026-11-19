"""Single-revision A/B improvement: evaluate A, revise once, generate and evaluate B."""

from __future__ import annotations

from EVA.ark import ArkClient
from EVA.config import Settings, get_settings
from EVA.improvement.repair import all_requirements_pass
from EVA.improvement.rewriter import FeedbackPromptRewriter
from EVA.io.storage import create_run_dir, write_json
from EVA.pipeline import EvaluationPipeline
from EVA.scoring.selection import compare_to_incumbent


class SimpleImprovementService:
    """Run exactly one revised generation, with no hidden candidates or retries."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        pipeline: EvaluationPipeline | None = None,
        rewriter: FeedbackPromptRewriter | None = None,
    ):
        self.settings = settings or get_settings()
        self.settings.validate()
        client = ArkClient(self.settings)
        self.pipeline = pipeline or EvaluationPipeline(self.settings)
        self.rewriter = rewriter or FeedbackPromptRewriter(client)

    async def improve(
        self,
        *,
        prompt: str,
        input_images: list[str] | None = None,
        target_texts: list[str] | None = None,
        generated_image: str | None = None,
        generation_size: str | None = None,
        generation_seed: int | None = None,
        case: str | None = None,
        stop_if_a_passes: bool = False,
    ) -> dict:
        input_images = input_images or []
        target_texts = target_texts or []
        run_id, run_dir = create_run_dir(self.settings.runs_dir, prefix="simple-improvement")

        # A may come from the user or from one new generation. Its route is the fixed ruler for B.
        a_result = await self.pipeline.run(
            prompt=prompt,
            input_images=input_images,
            target_texts=target_texts,
            generated_image=generated_image,
            include_advice=False,
            generation_size=generation_size,
            generation_seed=generation_seed,
        )
        a_evaluation = a_result.evaluations[0]
        if stop_if_a_passes and all_requirements_pass(a_evaluation.metrics):
            comparison = {
                "accepted": False,
                "improved": [],
                "degraded": [],
                "comparisons": [],
            }
            result = {
                "run_id": run_id,
                "case": case,
                "source": "user_provided" if generated_image else "generated",
                "original_prompt": prompt,
                "revised_prompt": prompt,
                "prompt_changed": False,
                "generation": {
                    "size": generation_size or self.settings.seedream_size,
                    "seed": generation_seed,
                    "guidance_scale": None,
                    "output_format": "png",
                    "watermark": self.settings.seedream_watermark,
                },
                "a": self._evaluation_fields(a_result),
                "b": None,
                "advice": None,
                "advisor_raw": None,
                "comparison": comparison,
                "improved": False,
                "skipped_b": True,
                "skip_reason": "original_a_already_passed",
                "output_dir": str(run_dir),
            }
            write_json(run_dir / "improvement.json", result)
            return result

        advice, advice_raw = await self.rewriter.revise(
            prompt=prompt,
            route=a_result.route,
            result=a_evaluation,
            input_images=input_images,
        )
        revised_prompt = advice.revised_generation_prompt

        # B1 is generated from the original inputs; only later repairs use a base image.
        b_result = await self.pipeline.run(
            prompt=revised_prompt,
            input_images=input_images,
            target_texts=target_texts,
            evaluation_route=a_result.route,
            include_advice=False,
            generation_size=generation_size,
            generation_seed=generation_seed,
        )
        b_evaluation = b_result.evaluations[0]
        comparison = compare_to_incumbent(a_evaluation.metrics, b_evaluation.metrics)
        result = {
            "run_id": run_id,
            "case": case,
            "source": "user_provided" if generated_image else "generated",
            "original_prompt": prompt,
            "revised_prompt": revised_prompt,
            "prompt_changed": revised_prompt.strip() != prompt.strip(),
            "generation": {
                "size": generation_size or self.settings.seedream_size,
                "seed": generation_seed,
                "guidance_scale": None,
                "output_format": "png",
                "watermark": self.settings.seedream_watermark,
            },
            "a": self._evaluation_fields(a_result),
            "b": self._evaluation_fields(b_result),
            "advice": advice.model_dump(mode="json"),
            "advisor_raw": advice_raw,
            "comparison": comparison,
            "improved": comparison["accepted"],
            "output_dir": str(run_dir),
        }
        write_json(run_dir / "improvement.json", result)
        return result

    @staticmethod
    def _evaluation_fields(result) -> dict:
        evaluation = result.evaluations[0]
        return {
            "image": evaluation.image.path,
            "metrics": evaluation.metrics,
            "failure_tags": evaluation.failure_tags,
            "output_dir": result.output_dir,
        }
