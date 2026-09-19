#!/bin/sh
set -eu
uv run --project apps/api --frozen ruff format --check apps/api infrastructure/scripts
uv run --project apps/api --frozen ruff check apps/api infrastructure/scripts
uv run --project apps/api --frozen mypy --config-file apps/api/pyproject.toml apps/api/src apps/api/tests infrastructure/scripts
uv run --project apps/api --frozen pytest apps/api/tests -m 'not integration' -q
for script in infrastructure/scripts/*.sh; do sh -n "$script"; done
