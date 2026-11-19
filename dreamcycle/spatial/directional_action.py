"""Neutral visual evidence for directional actions, scored by deterministic direction mapping."""

from __future__ import annotations

import asyncio
import json
from collections import Counter

from dreamcycle.ark import ArkClient
from dreamcycle.io.images import image_part, text_part

DIRECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "head_direction": {"type": "string", "minLength": 1},
        "limb_direction": {"type": "string", "minLength": 1},
        "subject_target_relation": {"type": "string", "minLength": 1},
        "trajectory_direction": {
            "type": "string",
            "enum": ["toward", "away", "unclear"],
        },
        "evidence": {"type": "string", "minLength": 1},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": [
        "head_direction",
        "limb_direction",
        "subject_target_relation",
        "trajectory_direction",
        "evidence",
        "confidence",
    ],
    "additionalProperties": False,
}

DIRECTION_SYSTEM_PROMPT = """
你是中立的动作方向证据提取器，不是任务符合度评分器。
只描述当前图像中可见的主体、目标、朝向和相对位置，不读取或迎合任何预期剧情。
输入会给出主体和目标；不要判断动作是否应该发生，也不要根据常见故事顺序猜测。

规则：
1. head_direction、limb_direction 分别写头部和前肢主要指向，使用画面左/右/上/下/
   朝向观察者/背向观察者/不明确等可见描述。
2. subject_target_relation 写主体位于目标的什么位置，目标开口或目的地位于主体哪一侧。
3. trajectory_direction 只在可见证据支持时给出：
   toward=主体朝向及运动趋势指向目标内部或目的地；
   away=主体朝向及运动趋势背离目标内部或目的地；
   unclear=静态姿态无法确定、朝向与位置矛盾或缺乏方向证据。
4. 腾空、位于箱口/门口/目标附近、跳起或四肢伸展本身都不能证明toward。
   不得因为图像看起来像某个动作名称就忽略头部、前肢与目标位置。
5. evidence 只写最终可见依据，不输出自我对话。
只返回符合 schema 的 JSON。
""".strip()


def expected_action_score(expected: str, observed: str) -> float:
    if expected not in {"toward", "away"}:
        raise ValueError(f"Unsupported expected direction: {expected}")
    if observed == "unclear":
        return 0.5
    return 1.0 if observed == expected else 0.0


class DirectionalActionJudge:
    def __init__(self, client: ArkClient, repeats: int = 10):
        self.client = client
        self.repeats = repeats

    async def evaluate(self, *, image: str, subject: str, target: str) -> dict:
        async def one_run(index: int) -> dict:
            content = [
                text_part(json.dumps({"subject": subject, "target": target}, ensure_ascii=False)),
                text_part("当前图片。只提取中立方向证据。"),
                image_part(image, detail="high", max_side=1536),
            ]
            raw = await self.client.chat_json(
                system=DIRECTION_SYSTEM_PROMPT,
                user_content=content,
                schema=DIRECTION_SCHEMA,
                schema_name="neutral_direction_evidence",
            )
            return {**raw, "_repeat_index": index}

        attempts = await asyncio.gather(*(one_run(index) for index in range(1, self.repeats + 1)))
        directions = Counter(item["trajectory_direction"] for item in attempts)
        highest = max(directions.values())
        leaders = [direction for direction, count in directions.items() if count == highest]
        if len(leaders) > 1:
            selected = "unclear"
        else:
            selected = leaders[0]
        evidence = next(
            (item["evidence"] for item in attempts if item["trajectory_direction"] == selected),
            "方向证据存在平票，无法确定。",
        )
        return {
            "direction": selected,
            "agreement": highest / self.repeats,
            "distribution": dict(directions),
            "evidence": evidence,
            "attempts": attempts,
        }
