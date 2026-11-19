"""RapidOCR adapter; the heavyweight engine is loaded lazily once."""

from __future__ import annotations

import asyncio
import threading
from pathlib import Path

from dreamcycle.ocr.metrics import score_texts
from dreamcycle.schemas import OCRScore


class OCRPlugin:
    def __init__(self):
        self._engine = None
        self._lock = threading.Lock()

    def _get_engine(self):
        if self._engine is None:
            from rapidocr_onnxruntime import RapidOCR

            self._engine = RapidOCR()
        return self._engine

    @staticmethod
    def _ordered_texts(result) -> list[str]:
        if not result:
            return []
        rows = sorted(
            result,
            key=lambda row: (
                min(point[1] for point in row[0]),
                min(point[0] for point in row[0]),
            ),
        )
        return [str(row[1]) for row in rows]

    async def score(self, image_path: str | Path, target_texts: list[str]) -> OCRScore:
        if not target_texts:
            return OCRScore(
                accuracy=0,
                ned=0,
                cer=0,
                f1=0,
                precision=0,
                recall=0,
                skipped_reason="No explicit target text was provided",
            )

        def run() -> list[str]:
            # Keep shared ONNX engine initialization/inference thread-safe.
            with self._lock:
                result, _ = self._get_engine()(str(image_path))
            return self._ordered_texts(result)

        predictions = await asyncio.to_thread(run)
        return score_texts(target_texts, predictions)
