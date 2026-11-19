"""Multi-label router using the configured Seed 2.1 Pro VLM endpoint."""

from __future__ import annotations

import json

from dreamcycle.ark import ArkClient
from dreamcycle.io.images import image_part, text_part
from dreamcycle.router.prompts import ROUTE_SCHEMA, ROUTER_SYSTEM_PROMPT
from dreamcycle.router.rules import normalize_route
from dreamcycle.schemas import RouteDecision


class Router:
    def __init__(self, client: ArkClient):
        self.client = client

    async def route(
        self,
        *,
        prompt: str,
        input_images: list[str],
        explicit_target_texts: list[str] | None = None,
    ) -> RouteDecision:
        explicit_target_texts = explicit_target_texts or []
        request = {
            "prompt": prompt,
            "input_image_count": len(input_images),
            "explicit_target_texts": explicit_target_texts,
            "note": "后续图片按输入顺序给出，均为用户输入图，不是生成结果。",
        }
        content = [text_part(json.dumps(request, ensure_ascii=False))]
        content.extend(image_part(path, detail="low", max_side=1024) for path in input_images)
        payload = await self.client.chat_json(
            system=ROUTER_SYSTEM_PROMPT,
            user_content=content,
            schema=ROUTE_SCHEMA,
            schema_name="seedream_route",
        )
        route = RouteDecision.model_validate(payload)
        return normalize_route(
            route,
            input_images=input_images,
            explicit_target_texts=explicit_target_texts,
            prompt=prompt,
        )
