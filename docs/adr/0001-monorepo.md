# 0001: Monorepo with native language tooling

Status: Proposed

Date: 2026-09-18

## Context

The browser, API, agent and plugin evolve one public contract but have different language toolchains.

## Decision

Keep apps/web, apps/api, agents/host-agent, integrations/minecraft-paper and packages/schemas in one repository. Use pnpm, Python tooling, Go modules and Gradle locally; share schemas and fixtures rather than cross-language business code.

## Alternatives

Separate repositories add protocol coordination overhead. A monorepo orchestration framework adds complexity before build scale warrants it.

## Consequences

Atomic contract reviews and shared CI become easier; path-based CI must still run dependent contract checks. Keep secrets/build artifacts out of version control.

## Validation

A clean checkout builds each component and contract generation is deterministic.

Related: [architecture](../architecture.md), [security](../security.md), [versions](../dependencies.md).
