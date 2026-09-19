#!/bin/sh
# Local disposable smoke test of the standalone production configuration.
set -eu
export COMPOSE_PROJECT_NAME="platform-production-test-$$"
verification_dir=$(mktemp -d)
export COMPOSE_ENV_FILES="$verification_dir/.env"
export PUBLIC_DOMAIN=http://localhost
export ACME_EMAIL=ops@example.com
export RELEASE_VERSION=foundation-test
python3 infrastructure/scripts/setup-dev.py --output "$COMPOSE_ENV_FILES"
# Inspect the unmodified production exposure before a local-only test override.
docker compose -f compose.production.yaml config --format json | python3 infrastructure/scripts/check-production.py
cat > "$verification_dir/smoke.yaml" <<'YAML'
services:
  caddy:
    ports: !override
      - "127.0.0.1:18080:80"
YAML
export COMPOSE_FILE="compose.production.yaml:$verification_dir/smoke.yaml"
cleanup() { docker compose down --volumes --remove-orphans; rm -rf "$verification_dir"; }
trap cleanup EXIT HUP INT TERM
docker compose build
docker compose run --rm --no-deps caddy caddy validate --config /etc/caddy/Caddyfile
docker compose up -d --wait postgres redis
docker compose --profile tools run --rm migrate
docker compose up -d --wait
curl --fail --silent http://localhost:18080/health/ready
curl --fail --silent http://localhost:18080/ > /dev/null
python3 infrastructure/scripts/measure-resources.py
# Redis is explicitly optional in this phase, even on fresh API/worker startup.
docker compose stop redis
docker compose restart api worker
docker compose up -d --wait api worker
curl --fail --silent http://localhost:18080/health/ready
# Confirm SIGTERM reaches the worker and completes cleanly.
docker compose stop worker
worker_id=$(docker compose ps --all --quiet worker)
exit_code=$(docker inspect --format '{{.State.ExitCode}}' "$worker_id")
[ "$exit_code" = 0 ]
printf '\nPASS: production builds, Caddy, health, Redis-optional startup and worker shutdown.\n'
