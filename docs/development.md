# Development

## Prerequisites and installation

Use Node 24.21.0, pnpm 12.4.2, Python 3.14, uv 0.12.16, Go 1.27.1 and Java 25.0.4.1+1. Gradle 9.7.1 is downloaded through the checksum-pinned wrapper. Install package managers using their official instructions, then:

```sh
uv sync --project apps/api --frozen
pnpm install --frozen-lockfile
```

On the implementation Mac, Python 3.14.4/Node 24.21.0 ran successfully; the container pins Python 3.14.7. Local downloaded toolchains live under ignored `.tools/`, which is not required in a normal checkout. If a sandbox blocks global caches, set `UV_CACHE_DIR`, `GOCACHE` and `GRADLE_USER_HOME` to writable local cache directories.

## Docker workflow

Run `infrastructure/scripts/dev-up.sh`. It creates `.env` only when absent, generates random local credentials without printing them, builds the images, starts PostgreSQL/Redis, runs one migration service, then starts API/worker/web. Open http://localhost:3000. Development ports bind only to 127.0.0.1: web 3000, API 8000, PostgreSQL 5432 and Redis 6379. Persistent database storage uses a named volume mounted at `/var/lib/postgresql` for PostgreSQL 18.

```sh
docker compose logs --tail 100 api worker
docker compose down
```

`down` preserves database data. `down --volumes` deletes it and should only be used for disposable environments. No simulator is included because no telemetry protocol exists in this phase. The shell contains an honest empty state rather than demo metrics.

## Native iteration

Start PostgreSQL/Redis with Compose, run the migration, then export your local runtime connection (use the generated app password, not the migration password):

```sh
export APP_DATABASE_URL='postgresql+psycopg://platform_app:<URL_ENCODED_LOCAL_PASSWORD>@127.0.0.1:5432/platform'
export APP_REDIS_URL='redis://127.0.0.1:6379/0'
uv run --project apps/api uvicorn control_plane.main:create_app --factory --host 127.0.0.1 --port 8000 --no-access-log
# In a separate terminal:
API_INTERNAL_URL=http://127.0.0.1:8000 pnpm web:dev
# Worker (separate terminal with APP_DATABASE_URL configured):
uv run --project apps/api python -m control_plane.worker
```

The API can start without a reachable database: liveness stays available and readiness returns a safe 503. Worker startup checks PostgreSQL and exits nonzero if unavailable. Redis is lazy/optional unless `APP_REDIS_REQUIRED=true`. The worker waits for signals and has no fake jobs.

## Environment variables

| Variable                                         | Use                                                                               |
| ------------------------------------------------ | --------------------------------------------------------------------------------- |
| `APP_ENVIRONMENT`                                | development/test/production; defaults to development                              |
| `APP_DATABASE_URL`                               | Required PostgreSQL psycopg URL; runtime identity only                            |
| `APP_REDIS_URL`                                  | Optional Redis URL                                                                |
| `APP_REDIS_REQUIRED`                             | Defaults false; true requires URL and successful ping for readiness               |
| `APP_DEPENDENCY_TIMEOUT_SECONDS`                 | Default 2, maximum 10; bounds readiness                                           |
| `MIGRATION_DATABASE_URL`                         | Alembic only; distinct migration identity                                         |
| `API_INTERNAL_URL`                               | Server-side web API endpoint; never sent as a browser secret                      |
| `POSTGRES_PASSWORD`                              | Compose bootstrap/admin credential                                                |
| `APP_DB_PASSWORD`, `MIGRATION_DB_PASSWORD`       | Distinct Compose role credentials; use random hex to avoid URL encoding ambiguity |
| `PUBLIC_DOMAIN`, `ACME_EMAIL`, `RELEASE_VERSION` | Required production edge/release configuration                                    |
| `TEST_DATABASE_URL`, `TEST_REDIS_URL`            | Real integration test services; absent values fail tests, not skip them           |
| `PLAYWRIGHT_CHANNEL`                             | Optional local installed browser channel; unset in Linux CI                       |

Native processes do not automatically load `.env`; Compose does. Never paste production secrets into shell history. Production rejects missing settings, placeholder database credentials and migration-role application URLs. Never print resolved Compose config with real credentials; use the supplied inspection pipeline.

## Test commands

```sh
infrastructure/scripts/check-python.sh
pnpm format:check
pnpm web:check
pnpm web:test
pnpm web:build
pnpm api:generate
pnpm api:drift
infrastructure/scripts/check-go.sh
integrations/minecraft-paper/gradlew -p integrations/minecraft-paper spotlessCheck test build --no-daemon
pnpm exec playwright install chromium
pnpm test:e2e
infrastructure/scripts/verify-compose.sh
```

`verify-compose.sh` creates an isolated test project and temporary credentials, builds services, applies migrations twice, runs PostgreSQL/Redis tests, verifies health, restores a sentinel and migration revision into a separate database, inspects production port configuration and measures container resources. It cleans up its test volumes on exit. Use a separate checkout and free ports 3000/5432/6379/8000. No production secrets are needed.

Formatting commands: `uv run --project apps/api ruff format apps/api infrastructure/scripts`, `pnpm format`, `gofmt -w agents/host-agent`, and `gradlew ... spotlessApply`. Generated client files are excluded from general formatting so generation remains byte-identical.

## Intel Mac notes

Validated host: Intel macOS 13.7.8. Current Playwright 1.63 Chromium downloads reject macOS 13; `PLAYWRIGHT_CHANNEL=chrome pnpm test:e2e` passed against the installed Chrome instead. CI installs the pinned browser on Linux. Prefer a supported macOS/Docker Desktop combination or run the container checks on the Linux EliteDesk; this task does not install or upgrade the host OS.

Next.js uses its supported webpack production builder because Turbopack build workers hit an OS port-binding restriction in this environment. Native builds/tests do not establish container compatibility. See [results](phase-1-results.md) for the exact verified and blocked checks.
