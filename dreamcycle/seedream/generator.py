"""Seedream generation and result download."""

from __future__ import annotations

import asyncio
from pathlib import Path

from dreamcycle.ark import ArkClient
from dreamcycle.config import Settings
from dreamcycle.io.images import image_to_data_uri
from dreamcycle.io.storage import download_image, write_json
from dreamcycle.schemas import GeneratedImage


class SeedreamGenerator:
    def __init__(self, client: ArkClient, settings: Settings):
        settings.validate(require_seedream=True)
        self.client = client
        self.settings = settings

    async def generate(
        self,
        *,
        prompt: str,
        input_images: list[str],
        run_dir: Path,
        size: str | None = None,
        seed: int | None = None,
        guidance_scale: float | None = None,
    ) -> list[GeneratedImage]:
        sources = [image_to_data_uri(path, max_side=2048) for path in input_images]
        image: str | list[str] | None = None
        if len(sources) == 1:
            image = sources[0]
        elif sources:
            image = sources
        raw_items = await self.client.generate_images(
            prompt=prompt,
            image=image,
            size=size,
            seed=seed,
            guidance_scale=guidance_scale,
        )

        async def download(index: int, item: dict) -> GeneratedImage:
            path = run_dir / f"generated-{index:02d}.png"
            await download_image(item["url"], path, timeout=self.settings.download_timeout_seconds)
            return GeneratedImage(path=str(path), url=item["url"], size=item.get("size"))

        images = await asyncio.gather(
            *(download(index, item) for index, item in enumerate(raw_items))
        )
        write_json(
            run_dir / "generation.json",
            {
                "model": self.settings.seedream_model,
                "size": size or self.settings.seedream_size,
                "seed": seed,
                "guidance_scale": guidance_scale,
                "output_format": "png",
                "response_format": "url",
                "watermark": self.settings.seedream_watermark,
                "prompt": prompt,
                "input_images": input_images,
                "outputs": [image.model_dump() for image in images],
            },
        )
        return images
