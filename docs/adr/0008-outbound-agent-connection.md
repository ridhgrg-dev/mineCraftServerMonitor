# 0008: Outbound authenticated agent WebSocket

Status: Proposed

Date: 2026-09-18

## Context

Customer hosts commonly sit behind NAT and must not expose control interfaces publicly.

## Decision

Agent initiates TLS-verified HTTPS/WSS to the control plane. Use locally generated Ed25519 identity and one-use challenge proof for short-lived scoped credentials. Version the protocol, persist duplicate protection and fence connections/bindings.

## Alternatives

Inbound SSH/RCON breaks the trust model. Polling remains a possible fallback but increases control latency. Managed mTLS PKI is viable but adds certificate lifecycle infrastructure for the initial deployment.

## Consequences

A persistent connection needs liveness, revocation, backpressure and reconnect handling. At-least-once delivery does not guarantee exactly-once external effects; ambiguous commands require reconciliation.

## Validation

Test replay, revoked live connection, version skew, reconnect, invalid binding and crash-window behavior with shared protocol fixtures.

Related: [architecture](../architecture.md), [security](../security.md), [versions](../dependencies.md).
