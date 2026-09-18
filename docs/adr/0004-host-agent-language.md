# 0004: Go host agent with local runtime adapters

Status: Proposed

Date: 2026-09-18

## Context

Customer hosts need a small portable daemon with predictable resource use and safe local operations.

## Decision

Use Go with explicit Docker, systemd, configured-process and simulator adapters. Local owner configuration binds opaque server IDs to exact targets. Keep transport, journal, telemetry and adapters separate.

## Alternatives

Python requires a managed runtime on customer machines. Rust is viable but adds implementation cost without a requirement that Go cannot meet.

## Consequences

Linux installs come first; platform-specific code uses build constraints. Docker access is privileged. Native macOS supports development/simulation, not systemd.

## Validation

Build Linux amd64/arm64 and Darwin amd64; test allowlist, crash recovery, duplicate delivery and reconnect.

Related: [architecture](../architecture.md), [security](../security.md), [versions](../dependencies.md).
