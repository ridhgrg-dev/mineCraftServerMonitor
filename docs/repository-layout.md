# Planned repository layout

Only documentation exists today. The following is a plan, not an inventory or runnable scaffold.

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
      adapters/                # Docker, systemd, configured process, simulator
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
