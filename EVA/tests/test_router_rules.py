from EVA.router.rules import normalize_route
from EVA.schemas import RouteDecision, TaskMode


def test_text_only_request_cannot_enable_edit_or_reference():
    route = RouteDecision(
        modes=[TaskMode.IMAGE_EDITING, TaskMode.REFERENCE_GENERATION],
        confidence=0.9,
    )
    normalized = normalize_route(
        route, input_images=[], explicit_target_texts=[], prompt="生成一只猫"
    )
    assert normalized.modes == [TaskMode.TEXT_TO_IMAGE]


def test_low_confidence_image_request_uses_edit_reference_union():
    route = RouteDecision(modes=[TaskMode.IMAGE_EDITING], confidence=0.2)
    normalized = normalize_route(
        route, input_images=["source.png"], explicit_target_texts=[], prompt="保留主体并换背景"
    )
    assert set(normalized.modes) == {
        TaskMode.IMAGE_EDITING,
        TaskMode.REFERENCE_GENERATION,
    }


def test_complex_composition_does_not_imply_structured_control():
    route = RouteDecision(modes=[TaskMode.TEXT_TO_IMAGE], confidence=0.9, needs_control=True)
    normalized = normalize_route(
        route,
        input_images=[],
        explicit_target_texts=[],
        prompt="必须恰好五只猫，左中右各一个人物",
    )
    assert normalized.needs_control is False


def test_explicit_text_forces_ocr_and_deduplicates_targets():
    route = RouteDecision(
        modes=[TaskMode.TEXT_TO_IMAGE],
        confidence=0.9,
        target_texts=["春日咖啡"],
    )
    normalized = normalize_route(
        route,
        input_images=[],
        explicit_target_texts=["春日咖啡", "MOON"],
        prompt="制作海报",
    )
    assert normalized.needs_ocr is True
    assert normalized.target_texts == ["春日咖啡", "MOON"]
