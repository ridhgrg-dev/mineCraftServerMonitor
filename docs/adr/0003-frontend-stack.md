# 0003: Next.js with strict TypeScript

Status: Proposed

Date: 2026-09-18

## Context

The product needs a polished accessible dashboard and public/authentication pages without duplicating backend policy.

## Decision

Use Next.js App Router, React, strict TypeScript and Tailwind. Prefer semantic HTML and a small accessible component layer. Generate the API client from OpenAPI; keep authorization in FastAPI.

## Alternatives

A client-only SPA is workable but gives up the requested Next stack. A large UI framework is not justified before requirements demonstrate need.

## Consequences

Server/client boundaries and cache policies require care. Tenant-sensitive responses must not enter shared caches. Add component and browser tests, and run lint separately from builds.

## Validation

Keyboard navigation, loading/error/empty states, type checks and production build pass; no user data leaks through shared rendering caches.

Related: [architecture](../architecture.md), [security](../security.md), [versions](../dependencies.md).
