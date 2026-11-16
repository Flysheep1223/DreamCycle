"""Dependency-free OCR string metrics, kept separate from the OCR engine."""

from __future__ import annotations

import unicodedata

from EVA.schemas import OCRScore


def normalize_text(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).split())


def levenshtein(left: str, right: str) -> int:
    if len(left) < len(right):
        left, right = right, left
    previous = list(range(len(right) + 1))
    for i, char_left in enumerate(left, start=1):
        current = [i]
        for j, char_right in enumerate(right, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (char_left != char_right),
                )
            )
        previous = current
    return previous[-1]


def _assign_candidates(
    targets: list[str], predictions: list[str]
) -> list[tuple[str, float, int] | None]:
    """Greedily assign each OCR line to at most one target, favoring high NED pairs."""
    pairs = []
    for target_index, target in enumerate(targets):
        for prediction_index, prediction in enumerate(predictions):
            distance = levenshtein(prediction, target)
            similarity = 1.0 - distance / max(len(prediction), len(target), 1)
            pairs.append((-similarity, distance, target_index, prediction_index))
    pairs.sort()
    assignments: list[tuple[str, float, int] | None] = [None] * len(targets)
    used_predictions = set()
    for negative_similarity, distance, target_index, prediction_index in pairs:
        if assignments[target_index] is not None or prediction_index in used_predictions:
            continue
        prediction = predictions[prediction_index]
        assignments[target_index] = (prediction, -negative_similarity, distance)
        used_predictions.add(prediction_index)
    return assignments


def score_texts(target_texts: list[str], predictions: list[str]) -> OCRScore:
    """Score target strings against OCR lines using exact, edit-distance and F1 views."""
    if not target_texts:
        raise ValueError("target_texts must not be empty")
    targets_norm = [normalize_text(text) for text in target_texts]
    predictions_norm = [normalize_text(text) for text in predictions if normalize_text(text)]
    details = []
    exact = 0
    total_distance = 0
    total_target_chars = 0
    total_ned = 0.0
    assignments = _assign_candidates(targets_norm, predictions_norm)
    for original, target, assignment in zip(target_texts, targets_norm, assignments, strict=True):
        prediction, similarity, distance = assignment or ("", 0.0, len(target))
        is_exact = normalize_text(prediction) == target
        exact += int(is_exact)
        total_distance += distance
        total_target_chars += len(target)
        total_ned += similarity
        details.append(
            {
                "target": original,
                "prediction": prediction,
                "exact": is_exact,
                "ned": similarity,
                "distance": distance,
            }
        )

    # One-to-one exact matching for end-to-end F1. Extra OCR lines count as FP.
    unused = set(range(len(predictions_norm)))
    tp = 0
    for target in targets_norm:
        match = next((index for index in unused if predictions_norm[index] == target), None)
        if match is not None:
            tp += 1
            unused.remove(match)
    fn = len(targets_norm) - tp
    fp = len(unused)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return OCRScore(
        accuracy=exact / len(targets_norm),
        ned=total_ned / len(targets_norm),
        cer=total_distance / max(total_target_chars, 1),
        f1=f1,
        precision=precision,
        recall=recall,
        targets=details,
        predictions=predictions_norm,
    )
