"""Dependency-free OCR string metrics, kept separate from the OCR engine."""

from __future__ import annotations

import unicodedata

from dreamcycle.schemas import OCRScore


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


def contains_target(prediction: str, target: str) -> bool:
    """Match a complete target within one OCR line without partial-word false positives."""
    if not target:
        return False
    start = 0
    while True:
        index = prediction.find(target, start)
        if index < 0:
            return False
        before = prediction[index - 1] if index else ""
        after_index = index + len(target)
        after = prediction[after_index] if after_index < len(prediction) else ""
        left_ok = not before or not target[0].isalnum() or not before.isalnum()
        right_ok = not after or not target[-1].isalnum() or not after.isalnum()
        if left_ok and right_ok:
            return True
        start = index + 1


def _assign_candidates(
    targets: list[str], predictions: list[str]
) -> list[tuple[str, float, int] | None]:
    """Allow distinct targets to share a line, then fuzzy-match remaining targets."""
    assignments: list[tuple[str, float, int] | None] = [None] * len(targets)
    used_pairs = set()
    used_predictions = set()
    for target_index, target in enumerate(targets):
        for prediction_index, prediction in enumerate(predictions):
            pair = (prediction_index, target)
            if pair not in used_pairs and contains_target(prediction, target):
                assignments[target_index] = (prediction, 1.0, 0)
                used_pairs.add(pair)
                used_predictions.add(prediction_index)
                break
    pairs = []
    for target_index, target in enumerate(targets):
        if assignments[target_index] is not None:
            continue
        for prediction_index, prediction in enumerate(predictions):
            if prediction_index in used_predictions:
                continue
            distance = levenshtein(prediction, target)
            similarity = 1.0 - distance / max(len(prediction), len(target), 1)
            pairs.append((-similarity, distance, target_index, prediction_index))
    pairs.sort()
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
        is_exact = contains_target(normalize_text(prediction), target)
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

    # Exact bounded targets can share one OCR line; unmatched lines count as FP.
    used_pairs = set()
    matched_lines = set()
    tp = 0
    for target in targets_norm:
        for index, prediction in enumerate(predictions_norm):
            pair = (index, target)
            if pair not in used_pairs and contains_target(prediction, target):
                tp += 1
                used_pairs.add(pair)
                matched_lines.add(index)
                break
    fn = len(targets_norm) - tp
    fp = len(predictions_norm) - len(matched_lines)
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
