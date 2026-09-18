# Phase 1 implementation plan

Status: ready for architecture review; implementation is not authorized by this document. Phase 1 means repository foundation, not the complete product MVP.

## Entry gate and scope

Review [decisions needing attention](review-decisions.md) and accept/revise the proposed ADRs. Re-inspect the repository before implementation. Establish runnable web/API/worker, PostgreSQL/Redis, migrations, native toolchains, container builds, test harnesses and CI. Identity, enrollment, telemetry/control and billing remain subsequent phases. Do not add fake production routes for those features.

## Reviewable increments

| Increment | Affected paths | Implementation | Acceptance |
| --- | --- | --- | --- |
| 1. Tooling | root workspace files, `.env.example`, `.gitignore`, `docs/dependencies.md` | Resolve exact stable patches, lock dependencies, native format/lint/type tools, secret exclusions | Reproducible clean install; licenses/source/reason recorded; no production defaults with secrets |
| 2. Backend | `apps/api`, `packages/schemas` | FastAPI app factory/settings, structured redacted errors/logging, liveness/readiness, DB/Redis wiring, migration base, worker shutdown | Health tests cover dependency loss and safe errors; migrations bootstrap on PostgreSQL; worker exits cleanly |
| 3. Web | `apps/web`, `packages/api-client` | Strict Next.js/React/Tailwind shell, accessible navigation/empty/error states, OpenAPI generation | Lint/types/component tests/build; client regeneration has no drift |
| 4. Agent/plugin harness | `agents/host-agent`, `integrations/minecraft-paper` | Compilable minimal binaries/plugin, version reporting, native tests, protocol fixture scaffolding | Go test/vet/build and Gradle test/build; no fake enrollment/control success paths |
| 5. Local runtime | `compose.yaml`, `infrastructure/docker`, simulator test tooling | Health-gated dependencies, volume persistence, migration command, optional isolated demo profile | Clean bootstrap in one or two documented commands; no Minecraft needed; demo never enabled in production |
| 6. Production foundation | `compose.production.yaml`, `infrastructure/caddy` | Explicit standalone production config, Caddy, private data network, non-root images, restart/health policies | Effective config publishes only Caddy; no source mounts/dev servers; missing secrets fail closed |
| 7. CI/docs | `.github/workflows`, README and operating docs | Required checks, image builds, dependency scans, developer workflow and initial DB backup/restore procedure | Fresh CI run passes; restore into separate database verifies data; commands match actual repository |

Use a clearly designated test/demo database for seed fixtures. Do not hard-code users or simulated metrics in production handlers. Later simulated-agent E2E must traverse the actual enrollment and command paths as those features become available.

## Verification matrix

| Layer | Required checks |
| --- | --- |
| Python | Ruff format/lint, strict type checking, pytest unit/API plus real PostgreSQL/Redis integration |
| Frontend | Formatter, ESLint separately from Next build, TypeScript, component tests, production build |
| Go | gofmt, go vet, go test (race detector on supported CI), build Linux amd64/arm64 and Darwin amd64 |
| Paper | Gradle wrapper integrity, formatter/static checks, JUnit and artifact build with matching Java |
| Contracts | JSON Schema fixture validation, generated OpenAPI/client drift check |
| Containers | Compose config validation, builds, health/smoke tests, private-port assertions |
| Browser | Playwright shell/navigation/accessibility smoke; auth and business E2E added with features |
| Supply chain | Lockfile checks, dependency vulnerability scan and image scan with documented exception policy |

Run each relevant formatter/linter/type checker/test/build, fix failures and record exact results at phase end. Security tests must exercise PostgreSQL and real role boundaries; SQLite is not a substitute. Required CI jobs cannot be silently skipped because credentials are missing; use isolated local service fixtures and provider test doubles.

## Risks and exit evidence

Version compatibility is provisional until packages resolve and builds run. Verify Intel macOS OS support and Docker resource use; containerized toolchains provide a fallback where native requirements differ. Match Paper/Java/Gradle versions before generating plugin files. Avoid migrations racing across service replicas. Persistent volumes are not backups. Production overrides must not accidentally inherit development port mappings.

Exit evidence includes exact resolved versions/locks, passing check commands, clean Compose boot, web/API readiness, database migration and restore results, container exposure inspection and measured local idle resource use. Report limitations rather than claim target scale. End with a concise review of changed files and unresolved issues before proceeding to Phase 2.
