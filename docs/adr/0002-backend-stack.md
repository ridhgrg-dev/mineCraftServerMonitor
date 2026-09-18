# 0002: FastAPI modular monolith

Status: Proposed

Date: 2026-09-18

## Context

The control plane needs typed HTTP APIs, persistent agent connections, relational transactions and background jobs.

## Decision

Use Python/FastAPI, Pydantic, SQLAlchemy and Alembic with PostgreSQL. Keep domain modules cohesive and API/worker in one codebase and image. Use a PostgreSQL transactional outbox with leased jobs initially.

## Alternatives

Microservices multiply deployments and distributed transactions. Django is viable but departs from the requested stack; an extra queue platform is unnecessary initially.

## Consequences

One deployable domain model reduces duplication. Blocking work must not run on the WebSocket event loop; workers need leases, idempotency and bounded retry behavior.

## Validation

API and worker integration tests prove transaction/outbox recovery; strict typing, migration and container builds pass.

Related: [architecture](../architecture.md), [security](../security.md), [versions](../dependencies.md).
