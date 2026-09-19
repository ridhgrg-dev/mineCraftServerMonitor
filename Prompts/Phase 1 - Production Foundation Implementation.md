Architecture review is complete and Phase 1 is approved.

Before implementing Phase 1, incorporate the following review decisions into the
existing architecture documentation where appropriate:

1. Redis remains approved for ephemeral coordination, but PostgreSQL remains the
   sole durable authority. Do not make basic application startup or ordinary
   development unnecessarily dependent on Redis beyond features that explicitly
   require it.

2. PostgreSQL RLS remains an approved defense-in-depth strategy. Phase 1 should
   establish the database roles, migration infrastructure, transaction-context
   approach, and tests needed for later RLS. Do not over-engineer RLS abstractions
   before tenant-owned tables arrive in Phase 2.

3. The Ed25519 agent authentication protocol is approved as designed. Before any
   implementation of agent enrollment/authentication in later phases, freeze
   canonical signed challenge encoding and byte-level cross-language fixtures.
   Do not casually alter the signed message format after fixtures exist.

4. Initial controllable runtime adapters will be Docker and systemd.
   Keep interfaces extensible for a future configured-process adapter, but do
   not implement generic/manual process lifecycle control during the initial
   product phases unless separately reviewed.

Mark the nine existing ADRs Accepted where these decisions do not conflict.
If an ADR needs wording updated to reflect the above decisions, update it before
implementation.

Then implement ONLY Phase 1 from docs/phase-1-plan.md.

PHASE 1 OBJECTIVE
=================

Create the production-quality repository foundation. Do not implement business
features from later phases such as users, organizations, enrollment, real agent
connections, Minecraft telemetry, server control, billing or Stripe.

Required outcomes:

- runnable monorepo
- locked dependency versions
- FastAPI application foundation
- worker foundation
- PostgreSQL
- Redis integration foundation
- Alembic migration infrastructure
- Next.js application foundation
- generated API client workflow
- Go host-agent compile/test harness
- Paper plugin compile/test harness
- shared protocol/schema fixture package
- Docker development environment
- production Docker Compose foundation
- Caddy production edge configuration
- CI
- tests
- documentation
- PostgreSQL backup/restore procedure

IMPLEMENTATION RULES
====================

Work through the increments defined in docs/phase-1-plan.md in order.

Do not generate fake business endpoints.

Permitted HTTP endpoints at this phase should be infrastructure-oriented, such
as:

- /health/live
- /health/ready
- OpenAPI/documentation in appropriate environments

Do not create placeholder endpoints that return fake users, fake servers,
fake telemetry, fake subscription states or fake command success.

DEPENDENCY LOCKING
==================

Resolve current stable mutually compatible versions using official
documentation and package registries.

Do not use floating "latest" image tags.

Record exact selected versions and rationale in docs/dependencies.md.

Generate and commit the appropriate lockfiles.

Verify:

- Intel macOS developer compatibility where applicable
- Linux amd64 production compatibility
- Linux arm64 build capability where required
- Python dependency/wheel availability
- Next.js / React / TypeScript peer compatibility
- Paper / Java / Gradle compatibility
- Go supported build targets

If the latest proposed version from the architecture documents is incompatible,
choose a supported stable alternative and document why.

BACKEND FOUNDATION
==================

Create apps/api using:

- FastAPI
- Pydantic settings
- SQLAlchemy
- Alembic
- PostgreSQL driver
- Redis client
- structured logging
- correlation/request IDs

Use an application factory.

Provide:

GET /health/live

This confirms only that the process is alive.

GET /health/ready

This checks required dependencies such as PostgreSQL and any dependency that is
actually required for readiness.

Do not expose secrets or raw connection errors.

Use the standard error envelope documented in docs/api-conventions.md.

Establish separate database identities/concepts for:

- migrations
- application runtime

Prepare the transaction context mechanism required for future tenant RLS, but do
not fabricate tenant tables merely to exercise it.

Tests must use PostgreSQL, not SQLite, for database integration behavior.

WORKER FOUNDATION
=================

Use the same Python domain code/image where appropriate.

Create a worker entrypoint with:

- clean startup
- structured logging
- dependency initialization
- signal handling
- graceful shutdown

Do not implement fake jobs.

It may perform a minimal internal heartbeat/lifecycle test only in test code.

FRONTEND FOUNDATION
===================

Create apps/web using:

- Next.js App Router
- React
- strict TypeScript
- Tailwind
- accessible semantic UI

Create a restrained professional application shell.

No fake operational statistics.

Provide sensible:

- loading state
- empty state
- error boundary
- 404 handling

Add a simple internal/system health view only if it uses real API state.

Generate the TypeScript API client reproducibly from FastAPI OpenAPI.

CI must detect generated-client drift.

HOST AGENT FOUNDATION
=====================

Create the Go module and binary structure described in repository-layout.md.

At this phase it should:

- compile
- expose version/build information
- support configuration loading
- support clean startup/shutdown
- have package boundaries for future enrollment, transport, journal, telemetry,
  adapters, backups and plugin integration

Do NOT implement real enrollment/authentication yet.

Do NOT implement cloud-controlled lifecycle operations yet.

Create interfaces and tests where useful, but no fake success paths.

Keep Docker and systemd as the approved initial runtime adapter targets.
Do not implement generic configured-process lifecycle control.

PAPER PLUGIN FOUNDATION
=======================

Create the Paper plugin project using the exact compatible Java/Paper/Gradle
versions resolved during dependency locking.

The plugin must:

- compile
- load as a valid plugin artifact
- expose plugin version metadata
- have testable package boundaries

Do not implement telemetry transmission yet.

Do not access NMS/private Minecraft internals.

Use documented Paper APIs only.

SHARED CONTRACTS
================

Create packages/schemas.

Establish:

- versioned JSON Schema location
- test fixture structure
- schema validation test tooling
- protocol version conventions

Do not prematurely implement the entire agent protocol.

Reserve a clearly documented location for the canonical Ed25519 challenge
fixtures required before Phase 3.

DOCKER DEVELOPMENT
==================

Create compose.yaml providing at minimum:

- API
- worker
- web
- PostgreSQL
- Redis

Provide an optional simulator/demo profile only if it is clearly isolated and
cannot accidentally run in production.

A developer should be able to start the environment using the documented
commands.

Do not require Minecraft for normal development.

Persist PostgreSQL data using a named volume.

Development-only exposed database/cache ports must bind to loopback, if exposed
at all.

PRODUCTION FOUNDATION
=====================

Create compose.production.yaml and Caddy configuration.

Production requirements:

- only Caddy publishes public HTTP/HTTPS ports
- PostgreSQL not public
- Redis not public
- API not directly public
- worker not public
- no development servers
- no source-code bind mounts
- production builds
- health checks
- restart policies
- persistent PostgreSQL storage
- private networks
- non-root containers where practical
- missing required production secrets/configuration causes startup failure

Do not run database migrations independently from every replica.
Provide an explicit documented migration/release command.

## SECRETS

Create .env.example containing placeholders only.

Never commit:

- actual passwords
- API keys
- private keys
- bearer tokens
- Stripe credentials
- webhook URLs containing secrets

Ensure .gitignore covers local secret/config variants appropriately.

## TESTING

Implement and run all Phase 1 applicable tests.

Required:

Python:
- formatting
- lint
- strict typing
- unit tests
- API tests
- PostgreSQL integration tests
- Redis integration tests where relevant

Frontend:
- formatting
- ESLint
- TypeScript
- component tests
- production build

Go:
- gofmt
- go vet
- go test
- race test where supported
- builds for required targets

Paper plugin:
- Gradle wrapper validation
- formatting/static checks
- unit tests
- artifact build

Contracts:
- schema validation tests
- fixture tests

Containers:
- image builds
- compose config validation
- health smoke test
- verify effective production config does not publish PostgreSQL or Redis

Browser:
- basic Playwright smoke test for application shell/navigation

CI/CD
=====

Create GitHub Actions workflows that run the required Phase 1 checks.

Use service containers for PostgreSQL/Redis where appropriate.

CI must not silently skip mandatory checks due to missing secrets.

Provider-dependent features are not implemented yet, so no production provider
credentials should be required.

Include dependency/security scanning that is practical at this stage.

DOCUMENTATION
=============

Update:

README.md
docs/development.md
docs/deployment.md
docs/database.md
docs/security.md
docs/dependencies.md

Add/document:

- exact clean checkout setup
- local development commands
- test commands
- Docker workflow
- Intel Mac development notes
- Linux EliteDesk deployment notes
- environment variables
- database migration procedure
- PostgreSQL backup procedure
- PostgreSQL restore procedure

Backup/restore instructions must be tested against a disposable database during
Phase 1.

RESOURCE BUDGET
===============

Because initial development/production may run on a Linux HP EliteDesk, measure
idle Docker Compose resource consumption at the end of Phase 1.

Report:

- memory by container
- total memory
- basic idle CPU observation
- disk footprint

Do not claim capacity from this measurement.

PHASE COMPLETION
================

Before declaring Phase 1 complete:

1. Run every applicable formatter.
2. Run every linter.
3. Run all type checks.
4. Run all unit/integration/component tests.
5. Run all builds.
6. Run Compose smoke testing.
7. Test PostgreSQL migration from empty database.
8. Test PostgreSQL backup and restore into a separate disposable database.
9. Inspect effective production Compose configuration for exposed ports.
10. Verify no committed secrets.
11. Verify generated API client has no drift.
12. Update documentation to match the commands that actually worked.

Create docs/phase-1-results.md containing:

- exact dependency versions selected
- exact commands run
- pass/fail results
- test counts
- build results
- Docker smoke-test result
- migration result
- backup/restore result
- production exposed-port inspection
- idle resource measurement
- known limitations
- unresolved issues
- recommendation whether Phase 2 is ready

Do not begin Phase 2.

Stop after Phase 1 and request review.
