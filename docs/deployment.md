# Production foundation deployment

Phase 1 is not yet cleared for production. The procedure below is implemented but awaits the Docker smoke/restore gate in [results](phase-1-results.md). No business features exist yet.

## Single Linux host

Use a maintained Linux distribution on the EliteDesk, Docker Engine with Compose and DNS pointing at the host. Permit inbound 80/443 only for the application. Keep host administration separately restricted. This Compose configuration is standalone: always use `-f compose.production.yaml`; do not merge it over the development file.

Create a private deployment environment file (mode 0600) with separate random hexadecimal `POSTGRES_PASSWORD`, `APP_DB_PASSWORD` and `MIGRATION_DB_PASSWORD`, plus real `PUBLIC_DOMAIN`, `ACME_EMAIL` and an immutable release identifier in `RELEASE_VERSION`. Environment files contain secrets; never commit them. Placeholder-only `.env.example` documents the names. PostgreSQL role passwords are initialized only on a new volume; changing environment values later does not rotate database passwords.

```sh
# From the release checkout with production .env installed:
docker compose -f compose.production.yaml config --format json | python3 infrastructure/scripts/check-production.py
docker compose -f compose.production.yaml build
docker compose -f compose.production.yaml up -d --wait postgres redis
# Explicit one-shot migration before application rollout:
docker compose -f compose.production.yaml --profile tools run --rm migrate
docker compose -f compose.production.yaml up -d --wait
```

Migrations do not run from API or worker startup. Future changes must preserve an application/schema compatibility window. Avoid automatic downgrade of data migrations during rollback; restore/reconcile according to a reviewed release plan.

Caddy proxies `/health/*` and `/api/*` to the API and all other routes to the web. Caddy persists certificates in named volumes and obtains HTTPS for the configured domain. API docs/OpenAPI are disabled in production. Internal health views disclose only availability, not credentials or raw errors.

API/worker run as UID 10001 with a read-only filesystem, writable `/tmp`, dropped capabilities and no-new-privileges. Web runs as the image's non-root node user. Official PostgreSQL/Redis entrypoints drop privileges as designed; Caddy needs its binding/certificate setup. Only Caddy has published ports. Caddy has no data-network access. Application/data networks are internal. No control-plane service mounts a Docker socket or source directory.

## Health and operation

API liveness tests only process response. API readiness requires PostgreSQL and Redis only when explicitly configured; optional Redis failure does not prevent basic service startup. Worker health marks successful initialization and a running idle process, not a claim of job throughput. Web health performs a real HTTP request. PostgreSQL and Redis use native probes. `restart: unless-stopped` restarts crashed processes; an unhealthy status alone does not restart a live container.

```sh
docker compose -f compose.production.yaml ps
docker compose -f compose.production.yaml logs --tail 100 api worker
COMPOSE_FILE=compose.production.yaml python3 infrastructure/scripts/measure-resources.py
```

Logs omit secrets/headers/connection errors and carry request IDs. Do not enable broad debug request logging in production. Build artifacts pin versions and multi-platform base image digests in `infrastructure/docker/image-manifests.json`; deployment image digests should also be captured when publishing a release.

## Backups and AWS migration

Follow [backup/restore](backups.md) and keep encrypted off-host archives plus separately protected configuration/credentials. A volume is not a backup. Recovery objectives remain provisional until rehearsal. Switching to EC2 initially requires host/DNS/configuration changes, not application changes. Managed PostgreSQL/Redis endpoints must use appropriate private networking and TLS. Database role bootstrap for a managed service must be performed by its administrator rather than the local image init hook.

There is no high availability claim and no demonstrated 5,000-server capacity. Measure container memory/CPU/disk on the actual EliteDesk before setting operating budgets.
