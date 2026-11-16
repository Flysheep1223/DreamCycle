"""Small official arkruntime wrapper used by the router, judge and generator."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from arkruntime import Ark

from EVA.config import Settings


class ArkClient:
    def __init__(self, settings: Settings):
        settings.validate(require_seedream=False)
        self.settings = settings
        self._client = Ark(
            base_url=settings.ark_base_url,
            api_key=settings.ark_api_key,
        )

    @staticmethod
    def _content_text(response: Any) -> str:
        content = response.choices[0].message.content
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for part in content:
                if isinstance(part, dict):
                    parts.append(str(part.get("text", "")))
                else:
                    parts.append(str(getattr(part, "text", "")))
            return "".join(parts)
        raise TypeError(f"Unsupported VLM content type: {type(content).__name__}")

    async def chat_json(
        self,
        *,
        system: str,
        user_content: list[dict],
        schema: dict,
        schema_name: str,
    ) -> dict:
        def request() -> Any:
            return self._client.chat.completions.create(
                model=self.settings.vlm_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_content},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": schema_name,
                        "description": "Structured image evaluation response",
                        "schema": schema,
                        "strict": True,
                    },
                },
                temperature=self.settings.vlm_temperature,
                thinking={"type": "disabled"},
                max_tokens=self.settings.vlm_max_tokens,
            )

        response = await asyncio.to_thread(request)
        text = self._content_text(response).strip()
        if text.startswith("```"):
            text = text.removeprefix("```json").removeprefix("```")
            text = text.removesuffix("```").strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"VLM returned invalid JSON: {text[:500]}") from exc

    async def generate_images(
        self,
        *,
        prompt: str,
        image: str | list[str] | None = None,
        size: str | None = None,
        seed: int | None = None,
        guidance_scale: float | None = None,
    ) -> list[dict[str, Any]]:
        kwargs: dict[str, Any] = {
            "model": self.settings.seedream_model,
            "prompt": prompt,
            "size": size or self.settings.seedream_size,
            "output_format": "png",
            "response_format": "url",
            "watermark": self.settings.seedream_watermark,
        }
        if seed is not None:
            kwargs["seed"] = seed
        if guidance_scale is not None:
            kwargs["guidance_scale"] = guidance_scale
        if image:
            kwargs["image"] = image
        response = await asyncio.to_thread(self._client.images.generate, **kwargs)
        results = []
        for item in response.data:
            if isinstance(item, dict):
                results.append({"url": item.get("url"), "size": item.get("size")})
            else:
                results.append(
                    {"url": getattr(item, "url", None), "size": getattr(item, "size", None)}
                )
        if not results or any(not item["url"] for item in results):
            raise ValueError("Seedream returned no downloadable image URL")
        return results
