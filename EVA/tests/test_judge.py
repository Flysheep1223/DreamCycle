import pytest
from PIL import Image

from EVA.judge import VLMJudge
from EVA.schemas import CheckItem, JudgeCheckResult, JudgeResult, RouteDecision, TaskMode


def test_reaggregate_aligns_answers_by_question_not_returned_id():
    route = RouteDecision(
        modes=[TaskMode.TEXT_TO_IMAGE],
        task_checklist=[
            CheckItem(id="t1", question="标题是否为春日咖啡？"),
            CheckItem(id="t2", question="背景是否有绿色植物？"),
        ],
    )
    judge = JudgeResult(
        task_score=0,
        pq=8,
        checks=[
            JudgeCheckResult(id="t2", question="标题是否为春日咖啡？", score=1),
            JudgeCheckResult(id="t1", question="背景是否有绿色植物？", score=0.5),
        ],
    )
    result = VLMJudge._reaggregate(route, judge)
    assert [check.id for check in result.checks] == ["t1", "t2"]
    assert result.task_score == 0.75
    assert result.checks[1].score == 0.5


def test_reaggregate_accepts_close_paraphrase():
    route = RouteDecision(
        modes=[TaskMode.IMAGE_EDITING],
        preservation_checklist=[CheckItem(id="p1", question="角色数量是否仍为3名，没有增减？")],
    )
    judge = JudgeResult(
        task_score=1,
        preservation_score=None,
        pq=8,
        checks=[
            JudgeCheckResult(
                id="p1",
                question="画面中是否保持3名角色，数量没有变化？",
                score=1,
            )
        ],
    )
    result = VLMJudge._reaggregate(route, judge)
    assert result.preservation_score == 1
    assert result.checks[0].question == "角色数量是否仍为3名，没有增减？"


class RetryClient:
    def __init__(self):
        self.calls = []

    async def chat_json(self, *, system, user_content, schema, schema_name):
        self.calls.append(system)
        if len(self.calls) == 1:
            checks = []
        else:
            checks = [
                {
                    "id": "t1",
                    "question": "标题是否为春日咖啡？",
                    "score": 1,
                    "reason": "文字正确",
                }
            ]
        return {
            "task_score": 1,
            "preservation_score": None,
            "pq": 8,
            "checks": checks,
            "edit": None,
            "reference": None,
            "failure_tags": [],
        }


@pytest.mark.asyncio
async def test_judge_retries_once_when_checklist_is_incomplete(tmp_path):
    image_path = tmp_path / "image.png"
    Image.new("RGB", (32, 32), "white").save(image_path)
    route = RouteDecision(
        modes=[TaskMode.TEXT_TO_IMAGE],
        task_checklist=[CheckItem(id="t1", question="标题是否为春日咖啡？")],
    )
    client = RetryClient()
    result, raw = await VLMJudge(client).evaluate(
        prompt="海报",
        route=route,
        input_images=[],
        generated_image=str(image_path),
    )
    assert result.task_score == 1
    assert raw["_attempt"] == 2
    assert len(raw["_previous_failed_attempts"]) == 1
    assert len(client.calls) == 2


class MalformedThenValidClient(RetryClient):
    async def chat_json(self, *, system, user_content, schema, schema_name):
        self.calls.append(system)
        if len(self.calls) == 1:
            raise ValueError("VLM returned invalid JSON: truncated")
        return await super().chat_json(
            system=system,
            user_content=user_content,
            schema=schema,
            schema_name=schema_name,
        )


@pytest.mark.asyncio
async def test_judge_retries_malformed_json(tmp_path):
    image_path = tmp_path / "image.png"
    Image.new("RGB", (32, 32), "white").save(image_path)
    route = RouteDecision(
        modes=[TaskMode.TEXT_TO_IMAGE],
        task_checklist=[CheckItem(id="t1", question="标题是否为春日咖啡？")],
    )
    client = MalformedThenValidClient()
    result, raw = await VLMJudge(client).evaluate(
        prompt="海报",
        route=route,
        input_images=[],
        generated_image=str(image_path),
    )
    assert result.task_score == 1
    assert raw["_attempt"] == 2
    assert "error" in raw["_previous_failed_attempts"][0]
