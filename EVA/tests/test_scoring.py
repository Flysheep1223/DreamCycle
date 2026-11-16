from EVA.schemas import (
    CheckItem,
    GeneratedImage,
    JudgeCheckResult,
    JudgeResult,
    OCRScore,
    ReferenceScore,
    RouteDecision,
    TaskMode,
)
from EVA.scoring import ScoreReporter


def test_reporter_keeps_separated_metrics_without_total_score():
    result = ScoreReporter.report(
        image=GeneratedImage(path="sample.png"),
        route=RouteDecision(modes=[TaskMode.TEXT_TO_IMAGE]),
        judge=JudgeResult(task_score=0.8, pq=8.0),
        judge_raw={},
        ocr=None,
    )
    assert result.metrics["task_score"] == 0.8
    assert result.metrics["perceptual_quality"] == 8.0
    assert result.metrics["preservation_score"] is None
    assert result.metrics["ocr"] is None
    assert "custom_overall" not in result.metrics
    assert "strict_overall" not in result.metrics
    assert "weights" not in result.metrics


def test_reference_scores_keep_their_original_zero_to_four_units():
    result = ScoreReporter.report(
        image=GeneratedImage(path="sample.png"),
        route=RouteDecision(modes=[TaskMode.REFERENCE_GENERATION]),
        judge=JudgeResult(
            task_score=1.0,
            pq=8.0,
            reference=ReferenceScore(cp=2.5, pf=4.0),
        ),
        judge_raw={},
        ocr=None,
    )
    assert result.metrics["reference"] == {"cp": 2.5, "pf": 4.0}
    assert result.metrics["preservation_score"] is None


def test_requirement_statistics_are_reported_separately():
    route = RouteDecision(
        modes=[TaskMode.TEXT_TO_IMAGE],
        task_checklist=[
            CheckItem(id="a", question="对象A是否存在？"),
            CheckItem(id="b", question="对象B是否存在？"),
        ],
    )
    judge = JudgeResult(
        task_score=0.625,
        pq=10,
        checks=[
            JudgeCheckResult(id="a", question="对象A是否存在？", score=1),
            JudgeCheckResult(id="b", question="对象B是否存在？", score=0.25),
        ],
    )
    result = ScoreReporter.report(
        image=GeneratedImage(path="sample.png"),
        route=route,
        judge=judge,
        judge_raw={},
        ocr=None,
    )
    assert result.metrics["task_score"] == 0.625
    assert result.full_requirement_rate == 0.5
    assert result.minimum_requirement_score == 0.25


def test_ocr_and_layout_remain_independent_metrics():
    ocr = OCRScore(accuracy=1, ned=1, cer=0, f1=0.25, precision=0.25, recall=1)
    route = RouteDecision(
        modes=[TaskMode.TEXT_TO_IMAGE],
        needs_ocr=True,
        no_extra_text=True,
        input_warnings=["示例警告"],
    )
    result = ScoreReporter.report(
        image=GeneratedImage(path="sample.png"),
        route=route,
        judge=JudgeResult(task_score=1, text_layout_score=0.8, pq=10),
        judge_raw={},
        ocr=ocr,
    )
    assert result.metrics["ocr"]["accuracy"] == 1
    assert result.metrics["ocr"]["f1"] == 0.25
    assert result.metrics["text_layout_score"] == 0.8
    assert "text" not in result.metrics
    assert result.raw_scores["input_warnings"] == ["示例警告"]
