import pytest

from EVA.ocr import levenshtein, normalize_text, score_texts


def test_levenshtein_and_unicode_normalization():
    assert levenshtein("春色满圆", "春色满园") == 1
    assert levenshtein("春色园", "春色满园") == 1
    assert normalize_text("  春日　咖啡 ") == "春日 咖啡"


def test_ocr_metrics_cover_exact_ned_cer_and_f1():
    targets = ["春色满园"] * 4
    predictions = ["春色满园", "春色满圆", "春色园", "春色满园呀"]
    result = score_texts(targets, predictions)
    assert result.accuracy == 0.25
    assert result.ned == pytest.approx(0.825)
    assert result.cer == pytest.approx(0.1875)
    assert result.precision == 0.25
    assert result.recall == 0.25
    assert result.f1 == 0.25


def test_missing_ocr_output_is_not_dropped_from_targets():
    result = score_texts(["必须出现"], [])
    assert result.accuracy == 0
    assert result.ned == 0
    assert result.cer == 1
    assert result.recall == 0
