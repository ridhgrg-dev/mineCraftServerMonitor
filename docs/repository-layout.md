# Planned repository layout

This is the full planned layout. Phase 1 now supplies web/API foundations, native harnesses, contracts, Compose, CI and scripts. Business-domain directories and simulator remain deferred; use `git ls-files` for the implemented inventory.

```text
/
  README.md
  Prompts/Initial Prompt.txt
  apps/
    web/                       # Next.js App Router, UI and component tests
    api/
      src/control_plane/
        identity/
        organizations/
        servers/
        agents/
        commands/
        telemetry/
        players/
        backups/
        alerts/
        billing/
        audit/
        jobs/                  # Worker entrypoint; same domain implementation
        core/                  # Settings, database, auth context, observability
      migrations/              # Alembic
      tests/                   # Unit, API, PostgreSQL integration/isolation
      pyproject.toml
      uv.lock
  agents/host-agent/
    cmd/host-agent/
    internal/
      enrollment/
      transport/
      journal/
      telemetry/
      adapters/                # Docker/systemd boundaries; implementation deferred
      backups/
      plugin/
    go.mod
    go.sum
  integrations/minecraft-paper/
    src/main/java/
    src/main/resources/
    src/test/java/
    build.gradle.kts
    gradle/wrapper/
  packages/
    schemas/                   # Agent/plugin JSON Schemas, fixtures, versions
    api-client/                # Generated TypeScript from backend OpenAPI
    shared/                    # Small UI-only shared utilities if needed
  infrastructure/
    docker/                    # Per-component multistage Dockerfiles
    caddy/
    scripts/                   # Bootstrap, backup/restore and release helpers
  tests/e2e/                   # Playwright with real API and simulated agent
  tools/simulator/            # Clearly isolated deterministic demo/test producer
  docs/
    adr/
    architecture.md
    product-requirements.md
    security.md
    database.md
    agent-protocol.md
    api-conventions.md
    dependencies.md
    repository-layout.md
    phase-1-plan.md
    review-decisions.md
    development.md             # Added with verified Phase 1 workflows
    deployment.md
    minecraft-plugin.md
    backups.md
    disaster-recovery.md
    billing.md
  .github/workflows/
  compose.yaml
  compose.production.yaml
  .env.example
  package.json
  pnpm-workspace.yaml
  pnpm-lock.yaml
```

Do not share Python/Go business logic through a TypeScript package. Share protocol contracts and conformance fixtures across languages. Generated API client changes must be reproducible and reviewed. Each runtime retains native build tooling; top-level tasks orchestrate it without adding a monorepo build framework initially.

## Approved Phase 1 review (2026-09-18)

Redis is optional for base readiness. PostgreSQL is the sole durable authority. Phase 1 establishes database roles and transaction-local tenant context without tenant tables; RLS policies follow in Phase 2. Docker and systemd are the initial controllable runtime targets; generic/manual process control is deferred. Freeze canonical Ed25519 challenge encoding and byte fixtures before Phase 3. Architecture review is complete; implement foundation only, then stop for review.
