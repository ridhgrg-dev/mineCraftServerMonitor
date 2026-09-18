# 0007: Redis for disposable coordination

Status: Proposed

Date: 2026-09-18

## Context

Rate limits and connection hints need fast expiring state, but command loss is unacceptable.

## Decision

Use Redis for throttles, short leases and routing notifications. Keep durable commands, jobs, sessions and audit in PostgreSQL. Verify selected Redis license/distribution before release.

## Alternatives

Database-only rate limits may become expensive; Redis as the sole task/command store risks data loss and complex recovery.

## Consequences

Loss of Redis may degrade availability but cannot erase accepted work. Sensitive mutations fail closed when rate limits cannot be safely enforced. Workers recover from PostgreSQL without relying on Pub/Sub delivery.

## Validation

Restart/flush Redis in integration tests: accepted commands survive, routing recovers and authentication throttling cannot be bypassed.

Related: [architecture](../architecture.md), [security](../security.md), [versions](../dependencies.md).
