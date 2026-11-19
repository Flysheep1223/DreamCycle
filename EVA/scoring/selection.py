"""Pareto checkpoint selection over separated metrics, without a weighted total."""

from __future__ import annotations

from typing import Any

# (dotted metric path, preferred direction). Missing metrics on both sides are ignored.
METRIC_RULES = (
    ("task_score", "higher"),
    ("g_pq", "higher"),
    ("text_layout_score", "higher"),
    ("full_requirement_rate", "higher"),
    ("ocr.cer", "lower"),
    ("ocr.f1", "higher"),
    ("edit.sc", "higher"),
    ("edit.e_pq", "higher"),
    ("reference.cppf", "higher"),
)
RANK_PATHS = (
    "task_score",
    "full_requirement_rate",
    "g_pq",
    "text_layout_score",
    "edit.sc",
    "edit.e_pq",
    "reference.cppf",
)
EPSILON = 1e-9


def metric_value(metrics: dict[str, Any], path: str) -> float | None:
    value: Any = metrics
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return float(value) if isinstance(value, int | float) else None


def compare_to_incumbent(incumbent: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    """Accept only a Pareto improvement: no guarded metric regresses, one improves."""
    improved = []
    degraded = []
    comparisons = []
    for path, direction in METRIC_RULES:
        before = metric_value(incumbent, path)
        after = metric_value(candidate, path)
        if before is None and after is None:
            continue
        if before is None or after is None:
            if before is not None:
                degraded.append(path)
            comparisons.append(
                {"metric": path, "before": before, "after": after, "change": "missing"}
            )
            continue
        improvement = after - before if direction == "higher" else before - after
        change = "same"
        if improvement > EPSILON:
            improved.append(path)
            change = "improved"
        elif improvement < -EPSILON:
            degraded.append(path)
            change = "degraded"
        comparisons.append(
            {
                "metric": path,
                "before": before,
                "after": after,
                "direction": direction,
                "improvement": improvement,
                "change": change,
            }
        )
    return {
        "accepted": bool(improved and not degraded),
        "improved": improved,
        "degraded": degraded,
        "comparisons": comparisons,
    }


def rank_key(metrics: dict[str, Any]) -> tuple[float, ...]:
    """Lexicographic tie-break only; this is never summed or normalized."""
    return tuple(
        metric_value(metrics, path) if metric_value(metrics, path) is not None else float("-inf")
        for path in RANK_PATHS
    )


def select_pareto_candidate(
    incumbent: dict[str, Any], candidates: list[dict[str, Any]]
) -> tuple[int | None, list[dict[str, Any]]]:
    decisions = []
    for index, candidate in enumerate(candidates):
        decisions.append(
            {
                "candidate_index": index,
                **compare_to_incumbent(incumbent, candidate.get("metrics", {})),
            }
        )
    accepted = [index for index, decision in enumerate(decisions) if decision["accepted"]]
    if not accepted:
        return None, decisions
    best = max(
        accepted,
        key=lambda index: (rank_key(candidates[index].get("metrics", {})), index),
    )
    return best, decisions
