FROM ghcr.io/astral-sh/uv:0.12.16 AS uv
FROM python:3.14.7-alpine3.24@sha256:016508ba505da24f7139765bc4bb669df4e88eb2f12eeadd571bf2f88d7533df AS base
COPY --from=uv /uv /usr/local/bin/uv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_LINK_MODE=copy
WORKDIR /app
COPY apps/api/pyproject.toml apps/api/uv.lock ./
COPY apps/api/src ./src
COPY apps/api/alembic.ini ./
COPY apps/api/migrations ./migrations
RUN uv sync --frozen --no-dev && adduser -D -u 10001 platform
ENV PATH="/app/.venv/bin:$PATH"
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "control_plane.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
