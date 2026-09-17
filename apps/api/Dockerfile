# THE HIVE LOGISTICS — FastAPI API and notification worker (single image).
# python:3.13-slim resolved on 2026-09-17 to 3.13.15-slim-trixie (multi-arch index digest).
FROM python:3.13-slim@sha256:9d2e5553305c7c7b0097999bb17187c69b921ccd6bc9d40e4bb5ebe652c00285

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:${PATH}"

RUN pip install --no-cache-dir uv==0.9.30 \
    && groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app

# Dependencies first (cacheable layer), strictly from uv.lock.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./
RUN uv sync --frozen --no-dev --no-editable

USER app

EXPOSE 8000

# exec: uvicorn becomes PID 1 and receives SIGTERM for graceful shutdown.
CMD ["sh", "-c", "exec uvicorn thl_api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
