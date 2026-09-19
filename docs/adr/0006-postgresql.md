# 0006: PostgreSQL as the durable source of truth

Status: Accepted

Date: 2026-09-18

## Context

Tenancy, commands, audit, billing and player sessions need relational integrity and transactional updates.

## Decision

Use PostgreSQL with normalized tables, composite tenant foreign keys, application authorization and FORCE RLS on tenant tables. Partition high-volume samples and maintain rollup watermarks. Use separate runtime/migration roles.

## Alternatives

SQLite does not reproduce production isolation. Document storage weakens relational constraints. A dedicated time-series database is deferred until measurements justify it.

## Consequences

RLS requires transaction-local context and pooled-connection tests. Volume and partition maintenance are explicit operational responsibilities. JSONB is limited to genuinely variable metadata.

## Validation

Two-tenant tests cover API and worker paths; migrations, backup/restore and aggregation idempotency pass against real PostgreSQL.

Related: [architecture](../architecture.md), [security](../security.md), [versions](../dependencies.md).

## Review clarification

Phase 1 establishes runtime/migration roles and transaction-local context, tested against PostgreSQL. Tenant tables and RLS policies arrive in Phase 2; no artificial tenant tables or policy framework in Phase 1.
