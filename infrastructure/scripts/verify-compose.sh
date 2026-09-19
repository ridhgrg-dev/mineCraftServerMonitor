#!/bin/sh
# Uses an isolated Compose project/database. Never point this at production.
set -eu
export COMPOSE_PROJECT_NAME="platform-foundation-test-$$"
verification_dir=$(mktemp -d)
export COMPOSE_ENV_FILES="$verification_dir/.env"
export COMPOSE_FILE=compose.yaml
cleanup() { docker compose down --volumes --remove-orphans; rm -rf "$verification_dir"; }
trap cleanup EXIT HUP INT TERM
python3 infrastructure/scripts/setup-dev.py --output "$COMPOSE_ENV_FILES"
docker compose up --build -d --wait postgres redis
docker compose build api worker migrate web
docker compose --profile tools run --rm migrate
# Confirm one-shot migrations are repeatable.
docker compose --profile tools run --rm migrate
# Generate URLs internally without printing secrets or shell-evaluating .env.
python3 infrastructure/scripts/run-integration.py
docker compose up -d --wait
curl --fail --silent http://127.0.0.1:8000/health/live
curl --fail --silent http://127.0.0.1:8000/health/ready
curl --fail --silent http://127.0.0.1:3000/ > /dev/null
# Put a sentinel in an explicitly disposable database so restore verifies data too.
docker compose exec -T postgres psql -U postgres -d platform -v ON_ERROR_STOP=1 -c "CREATE TABLE public.restore_probe (id integer PRIMARY KEY, value text NOT NULL); INSERT INTO public.restore_probe VALUES (1, 'foundation-restore-test');"
archive=$(COMPOSE_FILE=compose.yaml infrastructure/scripts/backup-db.sh)
COMPOSE_FILE=compose.yaml infrastructure/scripts/restore-db.sh "$archive" restore_foundation_test
value=$(docker compose exec -T postgres psql -U postgres -d restore_foundation_test -Atc 'SELECT value FROM public.restore_probe WHERE id=1')
[ "$value" = foundation-restore-test ]
revision=$(docker compose exec -T postgres psql -U postgres -d restore_foundation_test -Atc 'SELECT version_num FROM public.alembic_version')
[ "$revision" = 0001_foundation ]
docker compose exec -T postgres psql -U postgres -d platform -v ON_ERROR_STOP=1 -c 'DROP TABLE public.restore_probe'
PUBLIC_DOMAIN=example.com ACME_EMAIL=ops@example.com RELEASE_VERSION=0.1.0 docker compose -f compose.production.yaml config --format json | python3 infrastructure/scripts/check-production.py
python3 infrastructure/scripts/measure-resources.py
printf '\nPASS: Compose health, migration, integration and separate-database restore.\n'
