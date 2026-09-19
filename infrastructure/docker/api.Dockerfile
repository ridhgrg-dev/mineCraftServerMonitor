FROM ghcr.io/astral-sh/uv:0.12.16 AS uv
FROM python:3.14.7-slim-bookworm@sha256:bf5a06313080f516be80f78839d992270e7877dde4e2c345a41b84f862fbc28b AS base
COPY --from=uv /uv /usr/local/bin/uv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_LINK_MODE=copy
WORKDIR /app
COPY apps/api/pyproject.toml apps/api/uv.lock ./
COPY apps/api/src ./src
COPY apps/api/alembic.ini ./
COPY apps/api/migrations ./migrations
RUN uv sync --frozen --no-dev && useradd --uid 10001 --create-home platform
ENV PATH="/app/.venv/bin:$PATH"
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "control_plane.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
