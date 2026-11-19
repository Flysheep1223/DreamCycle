FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DREAMCYCLE_RUNS_DIR=/tmp/dreamcycle-runs

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
COPY dreamcycle ./dreamcycle
RUN uv sync --frozen --no-dev

EXPOSE 8010
CMD ["/app/.venv/bin/uvicorn", "dreamcycle.server.app:app", "--host", "0.0.0.0", "--port", "8010", "--workers", "1"]
