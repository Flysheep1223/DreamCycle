"""Async generation/routing fan-out followed by per-image parallel scoring."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from EVA.ark import ArkClient
from EVA.config import Settings, get_settings
from EVA.io.storage import create_run_dir, write_json
from EVA.judge import VLMJudge
from EVA.judge.errors import JudgeValidationError
from EVA.ocr import OCRPlugin
from EVA.reviewer import PromptAdvisor
from EVA.router import Router
from EVA.schemas import GeneratedImage, PipelineResult, RouteDecision
from EVA.scoring import ScoreReporter
from EVA.seedream import SeedreamGenerator


class EvaluationPipeline:
    def __init__(
        self,
        settings: Settings | None = None,
        *,
        router: Router | None = None,
        generator: SeedreamGenerator | None = None,
        judge: VLMJudge | None = None,
        ocr: OCRPlugin | None = None,
        advisor: PromptAdvisor | None = None,
    ):
        self.settings = settings or get_settings()
        client = ArkClient(self.settings)
        self.router = router or Router(client)
        self.generator = generator or SeedreamGenerator(client, self.settings)
        self.judge = judge or VLMJudge(client)
        self.ocr = ocr or OCRPlugin()
        self.advisor = advisor or PromptAdvisor(client)
        self.reporter = ScoreReporter()
        self._semaphore = asyncio.Semaphore(self.settings.workers)

    async def run(
        self,
        *,
        prompt: str,
        input_images: list[str] | None = None,
        target_texts: list[str] | None = None,
        generated_image: str | None = None,
        include_advice: bool | None = None,
        evaluation_route: RouteDecision | None = None,
        generation_size: str | None = None,
        generation_seed: int | None = None,
        generation_guidance_scale: float | None = None,
    ) -> PipelineResult:
        async with self._semaphore:
            return await self._run(
                prompt=prompt,
                input_images=input_images or [],
                target_texts=target_texts or [],
                generated_image=generated_image,
                include_advice=include_advice,
                evaluation_route=evaluation_route,
                generation_size=generation_size,
                generation_seed=generation_seed,
                generation_guidance_scale=generation_guidance_scale,
            )

    async def _run(
        self,
        *,
        prompt: str,
        input_images: list[str],
        target_texts: list[str],
        generated_image: str | None,
        include_advice: bool | None,
        evaluation_route: RouteDecision | None,
        generation_size: str | None,
        generation_seed: int | None,
        generation_guidance_scale: float | None,
    ) -> PipelineResult:
        run_id, run_dir = create_run_dir(self.settings.runs_dir)
        advise = self.settings.advisor_enabled if include_advice is None else include_advice
        write_json(
            run_dir / "request.json",
            {
                "prompt": prompt,
                "input_images": input_images,
                "target_texts": target_texts,
                "generated_image": generated_image,
                "include_advice": advise,
                "evaluation_route_provided": evaluation_route is not None,
                "generation_size": generation_size,
                "generation_seed": generation_seed,
                "generation_guidance_scale": generation_guidance_scale,
            },
        )
        generation_options = {}
        if generation_size is not None:
            generation_options["size"] = generation_size
        if generation_seed is not None:
            generation_options["seed"] = generation_seed
        if generation_guidance_scale is not None:
            generation_options["guidance_scale"] = generation_guidance_scale
        if generated_image:
            route = evaluation_route or await self.router.route(
                prompt=prompt,
                input_images=input_images,
                explicit_target_texts=target_texts,
            )
            images = [GeneratedImage(path=str(Path(generated_image).expanduser().resolve()))]
        elif evaluation_route is not None:
            route = evaluation_route
            images = await self.generator.generate(
                prompt=prompt,
                input_images=input_images,
                run_dir=run_dir,
                **generation_options,
            )
        else:
            route, images = await asyncio.gather(
                self.router.route(
                    prompt=prompt,
                    input_images=input_images,
                    explicit_target_texts=target_texts,
                ),
                self.generator.generate(
                    prompt=prompt,
                    input_images=input_images,
                    run_dir=run_dir,
                    **generation_options,
                ),
            )
        write_json(run_dir / "route.json", route.model_dump(mode="json"))
        evaluations = await asyncio.gather(
            *(
                self._evaluate_one(
                    index=index,
                    image=image,
                    prompt=prompt,
                    route=route,
                    input_images=input_images,
                    run_dir=run_dir,
                    include_advice=advise,
                )
                for index, image in enumerate(images)
            )
        )
        result = PipelineResult(
            run_id=run_id,
            route=route,
            evaluations=evaluations,
            output_dir=str(run_dir),
        )
        write_json(run_dir / "result.json", result.model_dump(mode="json"))
        return result

    async def _evaluate_one(
        self,
        *,
        index: int,
        image: GeneratedImage,
        prompt: str,
        route: RouteDecision,
        input_images: list[str],
        run_dir: Path,
        include_advice: bool,
    ):
        judge_task = self.judge.evaluate(
            prompt=prompt,
            route=route,
            input_images=input_images,
            generated_image=image.path,
        )
        ocr_task: Any = None
        if route.needs_ocr and route.target_texts:
            ocr_task = self.ocr.score(image.path, route.target_texts)
        try:
            if ocr_task:
                (judge, judge_raw), ocr = await asyncio.gather(judge_task, ocr_task)
            else:
                judge, judge_raw = await judge_task
                ocr = None
        except JudgeValidationError as exc:
            write_json(
                run_dir / f"judge-{index:02d}-error.json",
                {"error": str(exc), "raw": exc.raw},
            )
            raise
        write_json(run_dir / f"judge-{index:02d}.json", judge_raw)
        result = self.reporter.report(
            image=image,
            route=route,
            judge=judge,
            judge_raw=judge_raw,
            ocr=ocr,
        )
        if include_advice:
            try:
                advice, advice_raw = await self.advisor.review(
                    prompt=prompt,
                    route=route,
                    result=result,
                    input_images=input_images,
                )
                result = result.model_copy(update={"advice": advice})
                write_json(run_dir / f"advice-{index:02d}.json", advice_raw)
            except Exception as exc:  # noqa: BLE001 - optional audit must not lose valid scores.
                write_json(
                    run_dir / f"advice-{index:02d}-error.json",
                    {"error": f"{type(exc).__name__}: {exc}"},
                )
                result.raw_scores["advice_error"] = str(exc)
        write_json(run_dir / f"score-{index:02d}.json", result.model_dump(mode="json"))
        return result

    async def run_batch(self, requests: list[dict[str, Any]]) -> list[PipelineResult]:
        """Run independent requests concurrently, bounded by DREAMER_WORKERS."""
        return await asyncio.gather(*(self.run(**request) for request in requests))
