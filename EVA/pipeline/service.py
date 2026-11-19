"""Async generation/routing fan-out followed by per-image parallel scoring."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps

from EVA.ark import ArkClient
from EVA.config import Settings, get_settings
from EVA.io.images import is_url
from EVA.io.storage import create_run_dir, download_image, write_json
from EVA.judge import RepeatedVLMJudge, VLMJudge
from EVA.judge.errors import JudgeValidationError
from EVA.ocr import OCRPlugin
from EVA.reviewer import PromptAdvisor
from EVA.router import Router
from EVA.schemas import ActionRegion, CheckItem, GeneratedImage, PipelineResult, RouteDecision
from EVA.scoring import ScoreReporter
from EVA.seedream import SeedreamGenerator
from EVA.spatial.directional_action import DirectionalActionJudge, expected_action_score
from EVA.spatial.storyboard import region_for_panel


class EvaluationPipeline:
    def __init__(
        self,
        settings: Settings | None = None,
        *,
        router: Router | None = None,
        generator: SeedreamGenerator | None = None,
        judge: VLMJudge | RepeatedVLMJudge | None = None,
        ocr: OCRPlugin | None = None,
        advisor: PromptAdvisor | None = None,
        action_judge: DirectionalActionJudge | None = None,
    ):
        self.settings = settings or get_settings()
        client = ArkClient(self.settings)
        self.router = router or Router(client)
        self.generator = generator or SeedreamGenerator(client, self.settings)
        if judge is None:
            base_judge = VLMJudge(client)
            self.judge = (
                RepeatedVLMJudge(base_judge, repeats=self.settings.judge_repeats)
                if self.settings.judge_repeats > 1
                else base_judge
            )
        else:
            self.judge = judge
        self.ocr = ocr or OCRPlugin()
        self.advisor = advisor or PromptAdvisor(client)
        self.action_judge = action_judge or DirectionalActionJudge(
            client, repeats=self.settings.judge_repeats
        )
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

    async def _action_image(
        self, image_path: str, region: ActionRegion | None, check_id: str, run_dir: Path
    ) -> str:
        if region is None:
            return image_path
        source = image_path
        if is_url(source):
            source = str(
                await download_image(
                    source,
                    run_dir / f"action-source-{check_id}.png",
                    self.settings.download_timeout_seconds,
                )
            )

        def crop() -> str:
            destination = run_dir / f"action-{check_id}.png"
            with Image.open(source) as image:
                image = ImageOps.exif_transpose(image)
                left = round(region.x * image.width)
                top = round(region.y * image.height)
                right = round(min(1, region.x + region.width) * image.width)
                bottom = round(min(1, region.y + region.height) * image.height)
                image.crop((left, top, right, bottom)).save(destination, format="PNG")
            return str(destination)

        return await asyncio.to_thread(crop)

    async def _evaluate_directional_action(
        self, check: CheckItem, route: RouteDecision, image_path: str, run_dir: Path
    ) -> tuple[str, dict]:
        spec = check.action
        region = spec.region or region_for_panel(route.storyboard, spec.panel_index)
        crop = await self._action_image(image_path, region, check.id, run_dir)
        evidence = await self.action_judge.evaluate(
            image=crop,
            subject=spec.subject,
            target=spec.target,
        )
        return check.id, {
            "spec": spec.model_dump(mode="json"),
            "crop": crop,
            **evidence,
            "score": expected_action_score(spec.expected_direction, evidence["direction"]),
        }

    @staticmethod
    def _enforce_check_dependencies(route: RouteDecision, judge, judge_raw: dict):
        checks = {check.id: check for check in judge.checks}
        adjustments = []
        for item in [*route.task_checklist, *route.preservation_checklist]:
            if not item.depends_on:
                continue
            missing = [check_id for check_id in item.depends_on if check_id not in checks]
            if missing:
                raise ValueError(f"Check {item.id} has unknown dependencies: {missing}")
            parent = checks[item.id]
            limiting = min(
                (checks[check_id] for check_id in item.depends_on),
                key=lambda check: check.score,
            )
            if parent.score > limiting.score:
                before = parent.score
                parent.score = limiting.score
                parent.reason = (
                    f"联合检查受子项 {limiting.id}={limiting.score} 限制；"
                    + parent.reason
                )
                adjustments.append(
                    {
                        "parent": item.id,
                        "before": before,
                        "after": parent.score,
                        "limiting_child": limiting.id,
                    }
                )
        if adjustments:
            judge_raw["dependency_adjustments"] = adjustments
            return VLMJudge._reaggregate(route, judge)
        return judge

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
        directional_checks = [
            item
            for item in [*route.task_checklist, *route.preservation_checklist]
            if item.action is not None
        ]
        if directional_checks:
            evidence_items = await asyncio.gather(
                *(
                    self._evaluate_directional_action(item, route, image.path, run_dir)
                    for item in directional_checks
                )
            )
            evidence_by_id = dict(evidence_items)
            for check in judge.checks:
                if check.id not in evidence_by_id:
                    continue
                evidence = evidence_by_id[check.id]
                check.score = evidence["score"]
                check.reason = evidence["evidence"]
            judge = VLMJudge._reaggregate(route, judge)
            judge_raw["directional_actions"] = evidence_by_id
        judge = self._enforce_check_dependencies(route, judge, judge_raw)
        judge_raw["aggregated_result"] = judge.model_dump(mode="json")
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
