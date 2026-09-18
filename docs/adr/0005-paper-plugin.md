# 0005: Paper plugin as a local telemetry integration

Status: Proposed

Date: 2026-09-18

## Context

Host telemetry cannot expose reliable player sessions or game tick performance.

## Decision

Use Java and Gradle against documented Paper APIs, no NMS. Send bounded authenticated local telemetry to the agent; collect no chat or player IPs. Start with current Paper/Java compatibility and advertise unavailable metrics explicitly.

## Alternatives

Direct plugin-to-cloud credentials duplicate enrollment and widen exposure. NMS ties implementation to unstable internals. Kotlin is viable but adds a runtime/toolchain without clear benefit initially.

## Consequences

Game-thread-safe sampling and asynchronous network delivery need separate scheduling. Plugin absence must leave host monitoring usable. Container loopback requires explicit private networking configuration.

## Validation

Test event conversion, serialization, config and queue bounds; integration test supported Paper/Java versions and credential isolation.

Related: [architecture](../architecture.md), [security](../security.md), [versions](../dependencies.md).
