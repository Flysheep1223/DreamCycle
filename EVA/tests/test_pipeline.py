from pathlib import Path

import pytest
from PIL import Image

from EVA.config import Settings
from EVA.ocr import score_texts
from EVA.pipeline import EvaluationPipeline
from EVA.schemas import (
    AdviceReport,
    CheckItem,
    GeneratedImage,
    JudgeResult,
    RouteDecision,
    TaskMode,
)


class FakeRouter:
    async def route(self, *, prompt, input_images, explicit_target_texts):
        return RouteDecision(
            modes=[TaskMode.TEXT_TO_IMAGE],
            needs_ocr=True,
            confidence=0.95,
            target_texts=explicit_target_texts,
            task_checklist=[CheckItem(id="text", question="是否写出春日咖啡？")],
        )


class FakeGenerator:
    def __init__(self, image_path):
        self.image_path = image_path
        self.calls = []

    async def generate(
        self, *, prompt, input_images, run_dir, size=None, seed=None, guidance_scale=None
    ):
        self.calls.append({"size": size, "seed": seed, "guidance_scale": guidance_scale})
        return [GeneratedImage(path=str(self.image_path), size="64x64")]


class FakeJudge:
    async def evaluate(self, *, prompt, route, input_images, generated_image):
        result = JudgeResult(task_score=0.8, pq=8.0)
        return result, {"task_score": 0.8, "pq": 8.0}


class FakeOCR:
    async def score(self, image_path, target_texts):
        return score_texts(target_texts, ["春日咖啡"])


class FakeAdvisor:
    async def review(self, *, prompt, route, result, input_images):
        report = AdviceReport(
            overall_assessment="测试审计",
            generation_prompt_suggestions=["明确标题位置"],
            revised_generation_prompt="标题放在顶部：" + prompt,
            evaluation_prompt_suggestions=["增加额外乱码检查"],
            possible_judge_errors=[],
            confidence=0.9,
        )
        return report, report.model_dump()


@pytest.mark.asyncio
async def test_pipeline_runs_generation_judge_and_ocr(tmp_path: Path):
    image_path = tmp_path / "generated.png"
    Image.new("RGB", (64, 64), "white").save(image_path)
    settings = Settings(
        ark_api_key="test-only",
        vlm_model="fake-vlm",
        seedream_model="fake-seedream",
        runs_dir=tmp_path / "runs",
        workers=1,
        advisor_enabled=False,
    )
    generator = FakeGenerator(image_path)
    pipeline = EvaluationPipeline(
        settings,
        router=FakeRouter(),
        generator=generator,
        judge=FakeJudge(),
        ocr=FakeOCR(),
    )
    result = await pipeline.run(
        prompt="海报",
        target_texts=["春日咖啡"],
        generation_size="64x64",
        generation_seed=7,
        generation_guidance_scale=2.5,
    )
    evaluation = result.evaluations[0]
    assert evaluation.metrics["ocr"]["accuracy"] == 1.0
    assert evaluation.metrics["task_score"] == 0.8
    assert generator.calls == [{"size": "64x64", "seed": 7, "guidance_scale": 2.5}]
    assert (Path(result.output_dir) / "result.json").is_file()
    assert (Path(result.output_dir) / "route.json").is_file()


class NoCallRouter:
    async def route(self, **kwargs):
        raise AssertionError("evaluation_route 存在时不应重新调用路由器")


@pytest.mark.asyncio
async def test_pipeline_uses_fixed_evaluation_route(tmp_path: Path):
    image_path = tmp_path / "generated.png"
    Image.new("RGB", (64, 64), "white").save(image_path)
    fixed_route = RouteDecision(modes=[TaskMode.TEXT_TO_IMAGE])
    settings = Settings(
        ark_api_key="test-only",
        vlm_model="fake-vlm",
        seedream_model="fake-seedream",
        runs_dir=tmp_path / "runs",
        workers=1,
        advisor_enabled=False,
    )
    pipeline = EvaluationPipeline(
        settings,
        router=NoCallRouter(),
        generator=FakeGenerator(image_path),
        judge=FakeJudge(),
        ocr=FakeOCR(),
    )
    result = await pipeline.run(
        prompt="固定评估标准",
        generated_image=str(image_path),
        evaluation_route=fixed_route,
    )
    assert result.route is fixed_route


@pytest.mark.asyncio
async def test_pipeline_saves_independent_prompt_advice(tmp_path: Path):
    image_path = tmp_path / "generated.png"
    Image.new("RGB", (64, 64), "white").save(image_path)
    settings = Settings(
        ark_api_key="test-only",
        vlm_model="fake-vlm",
        seedream_model="fake-seedream",
        runs_dir=tmp_path / "runs",
        workers=1,
        advisor_enabled=True,
    )
    pipeline = EvaluationPipeline(
        settings,
        router=FakeRouter(),
        generator=FakeGenerator(image_path),
        judge=FakeJudge(),
        ocr=FakeOCR(),
        advisor=FakeAdvisor(),
    )
    result = await pipeline.run(prompt="海报", target_texts=["春日咖啡"])
    evaluation = result.evaluations[0]
    assert evaluation.advice is not None
    assert evaluation.advice.revised_generation_prompt.startswith("标题放在顶部")
    assert (Path(result.output_dir) / "advice-00.json").is_file()
