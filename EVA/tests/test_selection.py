from EVA.scoring.selection import compare_to_incumbent, select_pareto_candidate


def metrics(task=0.8, pq=8.0, full=0.7, minimum=0.5, ned=0.9):
    return {
        "task_score": task,
        "preservation_score": 1.0,
        "perceptual_quality": pq,
        "text_layout_score": 1.0,
        "full_requirement_rate": full,
        "minimum_requirement_score": minimum,
        "ocr": {
            "accuracy": 1.0,
            "ned": ned,
            "cer": 1.0 - ned,
            "precision": 1.0,
            "recall": 1.0,
            "f1": 1.0,
        },
    }


def test_pareto_selection_rejects_task_gain_that_damages_another_metric():
    decision = compare_to_incumbent(metrics(), metrics(task=0.95, pq=7.0))
    assert decision["accepted"] is False
    assert decision["improved"] == ["task_score"]
    assert decision["degraded"] == ["perceptual_quality"]


def test_pareto_selection_accepts_quality_gain_without_task_regression():
    decision = compare_to_incumbent(metrics(), metrics(pq=9.0))
    assert decision["accepted"] is True
    assert decision["improved"] == ["perceptual_quality"]


def test_pareto_selection_keeps_incumbent_when_every_candidate_regresses():
    candidates = [
        {"metrics": metrics(task=0.9, ned=0.8)},
        {"metrics": metrics(task=0.7, pq=9.0)},
        {"metrics": metrics()},
    ]
    selected, decisions = select_pareto_candidate(metrics(), candidates)
    assert selected is None
    assert [item["accepted"] for item in decisions] == [False, False, False]


def test_pareto_selection_uses_lexicographic_rank_not_a_total_score():
    candidates = [
        {"metrics": metrics(task=0.85, full=0.75, minimum=0.6)},
        {"metrics": metrics(task=0.9, full=0.8, minimum=0.6)},
    ]
    selected, decisions = select_pareto_candidate(metrics(), candidates)
    assert selected == 1
    assert all(item["accepted"] for item in decisions)
