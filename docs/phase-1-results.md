# Phase 1 verification results

Date: 2026-09-19. Scope: repository foundation only. Architecture review is incorporated and all nine ADRs are Accepted. No Phase 2 business features were added.

Status: **Phase 1 release accepted.** [Foundation CI run 35441774203](https://github.com/ridhgrg-dev/mineCraftServerMonitor/actions/runs/35441774203) passed at commit `518e87e9b99c90a8ea4f30dc33344d3b6a904b63`: Python, Go, Web, Paper, and Containers all passed. The blocking Anchore policy remains `fail-build: true` at `severity-cutoff: high`; it was not weakened.

## Final release evidence

| Item                        | Result                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| API runtime                 | `python:3.14.7-alpine3.24@sha256:016508ba505da24f7139765bc4bb669df4e88eb2f12eeadd571bf2f88d7533df`                                                                                                                                                                                                                                                                       |
| Web runtime                 | `node:24.21.0-alpine3.24@sha256:ebfe2f90462722a7a4de65e91990e97fe0d401c70e0e762c5b53302f905ec1c1`                                                                                                                                                                                                                                                                        |
| API security remediation    | Replaced Alpine `zlib 1.3.2-r0` with checksum-pinned zlib-ng 2.3.3 built in `ZLIB_COMPAT` mode; removed `apk` and the vulnerable package. The upstream zlib-ng test suite and API gzip/zlib factory smoke test passed.                                                                                                                                                   |
| Web security remediation    | Replaced Alpine `zlib 1.3.2-r0` with packaged zlib-ng 2.3.3, retained Node's required `libz.so.1` ABI with an explicit compatibility link, and removed `apk` and the vulnerable package. Node compression smoke passed.                                                                                                                                                  |
| Final API image digest      | `sha256:0123bde5b4282e2af33216c25f12c8f482e9622359d5cd4b48503075167a2cb1`                                                                                                                                                                                                                                                                                                |
| Final Web image digest      | `sha256:e314ff7a597b55813d63e01bb2c5d32442fe05fa50a72ed2b98a5238c80ecc1f`                                                                                                                                                                                                                                                                                                |
| Anchore result              | API: HIGH = 0, CRITICAL = 0. Web: HIGH = 0, CRITICAL = 0.                                                                                                                                                                                                                                                                                                                |
| Final functional validation | Hosted `verify-compose.sh` passed migrations, clean-database migration replay, integration checks, health checks, and backup/restore. Hosted `verify-production.sh` passed production Compose policy, Caddy/API/web smoke, Redis-optional restart, and worker shutdown. Web CI passed generated-client drift. Repository validation passed through all required CI jobs. |

## Selected versions

| Layer          | Exact selections                                                                                                                                                                          |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Web            | Node 24.21.0, pnpm 12.4.2, Next 16.3.5, React 19.3.0, TypeScript 6.0.3, Tailwind 4.3.3, ESLint 9.39.5                                                                                     |
| Python         | CPython 3.14.4 native / 3.14.7 container, uv 0.12.16, FastAPI 0.141.1, Pydantic 2.13.5, settings 2.15.0, SQLAlchemy 2.0.54, Alembic 1.20.0, Psycopg 3.3.6, redis-py 8.1.0, Uvicorn 0.53.0 |
| Go             | 1.27.1, standard library only                                                                                                                                                             |
| Paper          | API 26.2.build.124-stable, Temurin 25.0.4.1+1, Gradle 9.7.1, JUnit 6.0.3, Spotless 8.6.0                                                                                                  |
| Infrastructure | PostgreSQL 18.6, Redis 8.10.1, Caddy 2.11.4, Compose 5.5.1, Buildx 0.37.1                                                                                                                 |
| Browser/tests  | Playwright 1.63.0, Vitest 5.0.1, pytest 9.1.1, Ruff 0.16.8, mypy 2.3.1                                                                                                                    |

The complete direct dependency inventory, compatibility decisions and official references are in [dependencies](dependencies.md). Lockfiles contain transitive versions/hashes. Base image digests and Linux amd64/arm64 manifest verification are in [image manifests](../infrastructure/docker/image-manifests.json).

## Native checks completed

The following command names are reproducible after installing the pinned tools. In this session uv/pnpm/Go/Java were installed under ignored `.tools/`; local PATH selected those binaries. `UV_CACHE_DIR=.tools/uv-cache`, `GOCACHE=.tools/go-cache` and `GRADLE_USER_HOME=.tools/gradle-cache` keep sandbox caches writable.

| Exact command                                                                                                                                                                                                            | Result                                                                                            |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| `uv sync --project apps/api --frozen`                                                                                                                                                                                    | PASS, CPython 3.14 native dependencies installed                                                  |
| `uv build --project apps/api`                                                                                                                                                                                            | PASS, wheel and source distribution                                                               |
| `infrastructure/scripts/check-python.sh`                                                                                                                                                                                 | PASS, Ruff formatting/lint, strict mypy (14 source/test files), 14 unit/API/contract tests        |
| `pnpm install --frozen-lockfile`                                                                                                                                                                                         | PASS in Linux image build; final native frozen recheck recorded below                             |
| `pnpm web:check`                                                                                                                                                                                                         | PASS, ESLint and TypeScript                                                                       |
| `pnpm web:test`                                                                                                                                                                                                          | PASS, 4 component tests                                                                           |
| `pnpm web:build`                                                                                                                                                                                                         | PASS using `next build --webpack`; 2 static routes and dynamic `/system`                          |
| `pnpm api:drift`                                                                                                                                                                                                         | PASS, OpenAPI and generated TypeScript reproduced byte-for-byte                                   |
| `PLAYWRIGHT_CHANNEL=chrome pnpm test:e2e`                                                                                                                                                                                | PASS, 2 browser tests including navigation and 404 recovery; standalone production startup tested |
| `go vet ./...` from `agents/host-agent`                                                                                                                                                                                  | PASS                                                                                              |
| `go test ./...` and `go test -race ./...` from `agents/host-agent`                                                                                                                                                       | PASS, 3 top-level tests plus 4 configuration subtests                                             |
| `GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o ../../.tools/build/host-agent-linux-amd64 ./cmd/host-agent`                                                                                                           | PASS                                                                                              |
| `GOOS=linux GOARCH=arm64 CGO_ENABLED=0 go build -o ../../.tools/build/host-agent-linux-arm64 ./cmd/host-agent`                                                                                                           | PASS                                                                                              |
| `GOOS=darwin GOARCH=amd64 CGO_ENABLED=0 go build -o ../../.tools/build/host-agent-darwin-amd64 ./cmd/host-agent`                                                                                                         | PASS                                                                                              |
| `integrations/minecraft-paper/gradlew -p integrations/minecraft-paper spotlessCheck test build --no-daemon`                                                                                                              | PASS, 2 JUnit tests, Java lint warnings treated as errors, plugin JAR generated                   |
| SHA-256 comparison of Gradle wrapper JAR and distribution against official 9.7.1 release metadata                                                                                                                        | PASS                                                                                              |
| `uv export --project apps/api --frozen --no-dev --no-emit-project --format requirements-txt -o /tmp/mineops-api-requirements.txt` followed by `uv run --project apps/api pip-audit -r /tmp/mineops-api-requirements.txt` | PASS, no known vulnerabilities reported                                                           |
| `pnpm audit --prod --audit-level high`                                                                                                                                                                                   | PASS, no known vulnerabilities reported                                                           |
| `PUBLIC_DOMAIN=example.com ACME_EMAIL=ops@example.com RELEASE_VERSION=0.1.0 docker compose -f compose.production.yaml config --format json` piped to `python3 infrastructure/scripts/check-production.py`                | PASS, only Caddy 80/443, private networks, no bind mounts                                         |
| `docker compose -f compose.yaml config --quiet`                                                                                                                                                                          | PASS                                                                                              |

## Container, migration and restore evidence

`infrastructure/scripts/verify-compose.sh` passed on Colima Linux amd64. It built API/worker/migration/web/PostgreSQL images and pulled Redis, created a fresh named database volume, initialized separate roles, applied `0001_foundation` from an empty database, and applied `alembic upgrade head` again successfully.

All **4 real PostgreSQL/Redis integration tests passed**: transaction-local context is cleared after commit/rollback on a reused connection; runtime role cannot create in application/public schemas or bypass RLS; PostgreSQL readiness works without Redis; Redis ping/TTL/NX behavior works. Combined with native tests this is 18 passing Python tests.

API liveness/readiness and web HTTP checks passed. `backup-db.sh` produced a custom archive; `restore-db.sh` restored into new `restore_foundation_test`. Both the test-only sentinel value and `public.alembic_version = 0001_foundation` were verified. The test project and its volumes were then removed.

`infrastructure/scripts/verify-production.sh` also passed on Colima Linux amd64 against the digest-pinned Trixie runtime images. It validated Caddy, built the production services, returned `{"status":"ok"}` through the Caddy edge, measured idle resources, restarted API and worker with Redis stopped while readiness remained healthy, and verified a worker SIGTERM exits cleanly. It removed its disposable project, networks and volumes after completion.

On 2026-09-18, the current working tree rebuilt `server-operations-api:foundation-test` (`sha256:62ae19d1eee1014fe533bd5906f40977b562c4f28d68b99b1692026a530d6019`) and `server-operations-web:foundation-test` (`sha256:22da54461f199a6ef3012e501db49b2ca2ec385fe2139e0659578dba290b2cd1`). The isolated Grype 0.119.0 vulnerability database is valid at schema `v6.1.9`, built 2026-09-18T06:30:15Z. The scanner did not complete image cataloging through the local Colima socket within the available execution boundary, and offline image export did not complete either. Therefore this document makes no clean-scan claim for the rebuilt images.

## Resource observations

Environment: Intel macOS 13.7.8, Colima Linux x86_64, Docker daemon 29.5.2, 2 virtual CPUs, 3,116,601,344 bytes VM RAM. After a 10-second idle settling period, the development Compose stack reported:

| Container  | Memory         | CPU snapshot              |
| ---------- | -------------- | ------------------------- |
| API        | 84.20 MiB      | 0.49%                     |
| PostgreSQL | 63.55 MiB      | 0.00%                     |
| Redis      | 6.305 MiB      | 0.71%                     |
| Web        | 40.08 MiB      | 0.01%                     |
| Worker     | 67.66 MiB      | 0.01%                     |
| **Total**  | **261.80 MiB** | Point-in-time observation |

The PostgreSQL directory occupied 66,460 KiB. Docker reported 2.879 GB of images, 2.047 GB build cache, 73.56 MB local volumes and 77.82 kB container writable data across that daemon. These totals include shared base layers/build artifacts and are not the application's unique deployment size. Measurements exclude the Mac/VM overhead and are not a capacity claim.

The patched production stack measured 247.47 MiB total after idle: API 85.13 MiB, Caddy 12.50 MiB, PostgreSQL 35.14 MiB, Redis 5.277 MiB, web 41.57 MiB and worker 67.85 MiB. Its PostgreSQL volume occupied 47,520 KiB. These are point-in-time Colima observations, excluding Docker VM and host overhead.

## Issues resolved during implementation

- Latest ESLint 10/TypeScript 7 failed current Next lint peer requirements; selected exact compatible versions.
- pnpm 12 requires explicit `allowBuilds`; only sharp, esbuild and unrs-resolver are allowed.
- Turbopack hit an OS port-binding restriction; the supported webpack builder passed.
- Playwright's current bundled Chromium rejects macOS 13; installed Chrome passed native smoke tests. Linux CI uses bundled Chromium.
- Redis 8.10.2 had no official container tag when checked; selected the newest published 8.10.1 image with verified multi-platform digest.
- Docker was initially absent. After Colima became available, a stale Desktop credential helper and missing Buildx blocked pulls/builds. An ignored isolated Docker configuration and verified Buildx plugin resolved those tooling issues without changing global settings.

## Known limits and review gate

- No business authentication, tenant tables/RLS policies, enrollment, networked agents, telemetry, control, billing or world backups exist yet.
- Paper compiles against the public API and its artifact metadata is tested; a live Minecraft server has not been started.
- ARM Go binaries build; base container indexes advertise ARM64. An ARM host runtime has not been exercised.
- Native test dependencies emit two upstream deprecation warnings; Gradle reports deprecated features ahead of Gradle 10. These do not fail pinned-tool checks.
- Hosted CI run 35441774203 is the release acceptance record. It completed all five required jobs and its strict Anchore scans found no unresolved HIGH or CRITICAL findings in the final API and web images.
- Public ACME certificate issuance needs a real domain and has not been attempted against a user's deployment.

Phase 2 recommendation: begin only after Phase 1 review acceptance has been acknowledged.
