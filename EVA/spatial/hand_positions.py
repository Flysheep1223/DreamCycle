"""Coordinate-based hand/object checks that avoid asking a VLM for handedness."""

from __future__ import annotations

from pydantic import BaseModel

from EVA.ark import ArkClient
from EVA.io.images import image_part, text_part

BBOX = {
    "type": "array",
    "items": {"type": "number", "minimum": 0, "maximum": 1},
    "minItems": 4,
    "maxItems": 4,
}
SPATIAL_SCHEMA = {
    "type": "object",
    "properties": {
        "person_bbox": BBOX,
        "wrench_bbox": BBOX,
        "book_bbox": BBOX,
        "evidence": {"type": "string"},
    },
    "required": ["person_bbox", "wrench_bbox", "book_bbox", "evidence"],
    "additionalProperties": False,
}


class SpatialHandResult(BaseModel):
    person_center_x: float
    wrench_center_x: float
    book_center_x: float
    left_hand_wrench_correct: bool
    right_hand_book_correct: bool
    evidence: str


class SpatialHandJudge:
    def __init__(self, client: ArkClient):
        self.client = client

    @staticmethod
    def _center(bbox: list[float]) -> float:
        return (bbox[0] + bbox[2]) / 2

    async def evaluate(self, image_path: str) -> tuple[SpatialHandResult, dict]:
        system = (
            "你是视觉空间定位器。只标出指定物体的归一化矩形框，不判断左右手，不写推理过程。"
            "坐标均为0到1，x向右、y向下。框格式[x1,y1,x2,y2]，必须覆盖目标边缘。"
            "目标：画面右侧深色短发少女、她持有的扳手、她持有的红书。"
            "evidence最多40个汉字，只描述可见物体。"
        )
        raw = await self.client.chat_json(
            system=system,
            user_content=[
                text_part("标出人物、扳手和红书的bbox。"),
                image_part(image_path, detail="high", max_side=1536),
            ],
            schema=SPATIAL_SCHEMA,
            schema_name="hand_object_positions",
        )
        person_x = self._center(raw["person_bbox"])
        wrench_x = self._center(raw["wrench_bbox"])
        book_x = self._center(raw["book_bbox"])
        result = SpatialHandResult(
            person_center_x=person_x,
            wrench_center_x=wrench_x,
            book_center_x=book_x,
            left_hand_wrench_correct=wrench_x > person_x,
            right_hand_book_correct=book_x < person_x,
            evidence=raw["evidence"],
        )
        return result, raw
