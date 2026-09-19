# 0009: Docker Compose on a single Linux host

Status: Accepted

Date: 2026-09-18

## Context

Initial production runs on an EliteDesk and must later move to AWS without application rewrites.

## Decision

Use development and standalone production Compose configurations, with web/API/worker/PostgreSQL/Redis and Caddy at the production edge. Publish only Caddy ports; configure storage/endpoints/secrets externally.

## Alternatives

Kubernetes and managed cloud dependencies exceed MVP operational needs. Bare-metal installation makes reproducibility and migration harder.

## Consequences

Single-host failure causes downtime; persistent volumes need off-host backups. Build native target architectures and run release migrations once. AWS can initially use the same images on EC2.

## Validation

Inspect effective production config, build images, verify health/restart behavior and perform a database restore on a separate target.

Related: [architecture](../architecture.md), [security](../security.md), [versions](../dependencies.md).
