FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DREAMCYCLE_RUNS_DIR=/tmp/dreamcycle-runs \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_DEFAULT_TIMEOUT=120 \
    UV_HTTP_TIMEOUT=120

WORKDIR /app

RUN sed -i "s|deb.debian.org|mirrors.ustc.edu.cn|g" /etc/apt/sources.list.d/debian.sources
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
COPY dreamcycle ./dreamcycle
RUN uv sync --frozen --no-dev

EXPOSE 8010
CMD ["/app/.venv/bin/uvicorn", "dreamcycle.server.app:app", "--host", "0.0.0.0", "--port", "8010", "--workers", "1"]
