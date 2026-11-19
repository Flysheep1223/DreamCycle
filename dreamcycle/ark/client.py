"""Small official arkruntime wrapper used by the router, judge and generator."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from arkruntime import Ark

from dreamcycle.ark.validation import SchemaValidationError, validate_json_schema
from dreamcycle.config import Settings


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
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ]
        last_error = None
        for attempt in range(2):
            def request() -> Any:
                return self._client.chat.completions.create(
                    model=self.settings.vlm_model,
                    messages=messages,
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
            # VIEScore wraps JSON with ||V^=^V|| delimiters; parse only the JSON object.
            start, end = text.find("{"), text.rfind("}")
            if start >= 0 and end > start:
                text = text[start : end + 1]
            try:
                payload = json.loads(text)
                validate_json_schema(payload, schema)
                return payload
            except (json.JSONDecodeError, SchemaValidationError, TypeError) as exc:
                last_error = exc
                if attempt == 0:
                    messages.append(
                        {
                            "role": "user",
                            "content": (
                                f"上一响应未通过 {schema_name} 硬结构校验：{exc}。"
                                "请重新生成完整 JSON，只修复指出的字段，不得遗漏必填字段、"
                                "改变分数尺度、添加额外字段或返回解释性文字。"
                            ),
                        }
                    )
        raise ValueError(f"VLM response failed {schema_name} validation after retry: {last_error}")

    async def chat_text(self, messages: list[dict]) -> str:
        """Run a plain-text request for official Score: N protocols."""
        def request() -> Any:
            return self._client.chat.completions.create(
                model=self.settings.vlm_model,
                messages=messages,
                temperature=self.settings.vlm_temperature,
                thinking={"type": "disabled"},
                max_tokens=self.settings.vlm_max_tokens,
            )

        response = await asyncio.to_thread(request)
        return self._content_text(response).strip()

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
