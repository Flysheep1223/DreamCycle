from PIL import Image

from EVA.reviewer import PromptAdvisor
from EVA.schemas import GeneratedImage, JudgeResult, RouteDecision, TaskMode
from EVA.scoring import ScoreReporter


class TwoStageClient:
    def __init__(self):
        self.calls = []

    async def chat_json(self, *, system, user_content, schema, schema_name):
        self.calls.append({"schema_name": schema_name, "user_content": user_content})
        if schema_name == "evaluation_audit":
            return {
                "overall_assessment": "部分评分与图像证据不一致",
                "evaluation_prompt_suggestions": ["将左右手拆成独立检查项"],
                "additional_checks": [],
                "possible_judge_errors": ["右手红书可能被误判"],
                "confidence": 0.9,
            }
        return {
            "generation_prompt_suggestions": ["明确人物自身右手持伞"],
            "revised_generation_prompt": "保留全部原始要求，并明确人物自身右手持伞。",
        }


async def test_prompt_advice_is_independent_from_evaluation_audit(tmp_path):
    image_path = tmp_path / "image.png"
    Image.new("RGB", (32, 32), "white").save(image_path)
    route = RouteDecision(modes=[TaskMode.TEXT_TO_IMAGE])
    result = ScoreReporter.report(
        image=GeneratedImage(path=str(image_path)),
        route=route,
        judge=JudgeResult(task_score=0.5, pq=8),
        judge_raw={},
        ocr=None,
    )
    client = TwoStageClient()
    report, raw = await PromptAdvisor(client).review(
        prompt="上一轮草稿提示词",
        original_prompt="不可变的原始用户提示词",
        route=route,
        result=result,
        input_images=[],
    )
    assert len(client.calls) == 2
    first_text = client.calls[0]["user_content"][0]["text"]
    second_text = client.calls[1]["user_content"][0]["text"]
    assert "scores_and_reasons" in first_text
    assert "scores_and_reasons" not in second_text
    assert "task_score" not in second_text
    assert "original_user_prompt" in second_text
    assert "不可变的原始用户提示词" in second_text
    assert "current_draft_prompt" in second_text
    assert "上一轮草稿提示词" in second_text
    assert "possible_judge_errors" not in second_text
    assert report.revised_generation_prompt.startswith("保留全部原始要求")
    assert report.overall_assessment == "部分评分与图像证据不一致"
    assert raw["prompt_suggestion_excluded_context"]
    assert raw["prompt_revision_policy"]["name"] == "best_checkpoint_guarded_revision_v4"
    assert next(iter(report.model_dump())) == "generation_prompt_suggestions"


class OverlongClient(TwoStageClient):
    def __init__(self):
        super().__init__()
        self.suggestion_calls = 0

    async def chat_json(self, **kwargs):
        response = await super().chat_json(**kwargs)
        if kwargs["schema_name"] == "independent_prompt_suggestions":
            self.suggestion_calls += 1
            if self.suggestion_calls == 1:
                response["revised_generation_prompt"] = "长" * 500
        return response


async def test_prompt_advice_retries_an_overlong_revision(tmp_path):
    image_path = tmp_path / "image.png"
    Image.new("RGB", (32, 32), "white").save(image_path)
    route = RouteDecision(modes=[TaskMode.TEXT_TO_IMAGE])
    result = ScoreReporter.report(
        image=GeneratedImage(path=str(image_path)),
        route=route,
        judge=JudgeResult(task_score=0.5, pq=8),
        judge_raw={},
        ocr=None,
    )
    client = OverlongClient()
    report, raw = await PromptAdvisor(client).review(
        prompt="上一轮" * 100,
        original_prompt="简短但完整的原始需求",
        route=route,
        result=result,
        input_images=[],
    )
    policy = raw["prompt_revision_policy"]
    assert client.suggestion_calls == 2
    assert policy["length_retry"] is True
    assert policy["length_fallback"] is False
    assert policy["revised_prompt_characters"] <= policy["character_budget"]
    assert report.revised_generation_prompt.startswith("保留全部原始要求")
