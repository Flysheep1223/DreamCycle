"""Local FastAPI surface for realtime generation and scoring."""

from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from EVA.config import get_settings
from EVA.pipeline import EvaluationPipeline


class RunRequest(BaseModel):
    prompt: str = Field(min_length=1)
    input_images: list[str] = Field(default_factory=list)
    target_texts: list[str] = Field(default_factory=list)
    generated_image: str | None = None
    include_advice: bool | None = None


@lru_cache(maxsize=1)
def get_pipeline() -> EvaluationPipeline:
    return EvaluationPipeline()


app = FastAPI(title="Seedream EVA", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "settings": get_settings().public_dict()}


@app.post("/v1/evaluate")
async def evaluate(request: RunRequest) -> dict:
    try:
        result = await get_pipeline().run(**request.model_dump())
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result.model_dump(mode="json")
