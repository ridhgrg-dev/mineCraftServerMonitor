# Product requirements

Status: proposed, 2026-09-18. Source: [initial specification](../Prompts/Initial%20Prompt.txt).

## Product and scope

Provide independent server owners, communities and networks with monitoring and safe operations through a multi-tenant SaaS or self-hosted control plane. Separate a hosted dashboard/API, a Go host daemon and a Paper telemetry plugin. Minecraft is the first game adapter. No player automation, cheating, public customer control ports, generic remote shell, Kubernetes, Kafka or AI in the initial delivery.

Support a 2018 Intel MacBook Pro for development, a Linux EliteDesk for initial production and later AWS through configuration and storage adapters. Normal development must not run Minecraft. Target 1,000 organizations and 5,000 managed servers; this is a capacity validation target, not a proven capability.

## Functional requirements

| Area | Required behavior | Delivery |
| --- | --- | --- |
| Identity | Register, verify email, login/logout, reset password, rotating revocable sessions, throttling | Phase 2 |
| Organizations | Multiple memberships; OWNER, ADMIN, OPERATOR, VIEWER; invitations and server-side tenant isolation | Phase 2 |
| Onboarding | Server CRUD, expiring single-use enrollment, device identity, rotation/revocation | Phase 3 |
| Agent | Outbound TLS, reconnect/jitter, heartbeat, host CPU/RAM/disk/uptime, simulator | Phase 4 |
| Dashboard | Accurate health, last seen, Minecraft/agent/plugin status, responsive accessible UI | Phase 5 |
| Paper | Player counts, UUID/name, join/quit, TPS/MSPT when available, worlds and version | Phase 6 |
| Control | Docker/systemd start/stop/restart, typed allowlist, timeouts, durable command history | Phase 7 |
| Logs/events | Bounded sanitized operational events and opt-in filtered log tail | Phases 5–7 |
| Backups | Local destination, consistency policy, capacity check, overlap protection, size/status and retention | Phase 8 |
| Alerts | Offline/resource/TPS/MSPT/backup rules, duration, cooldown, dedup and recovery; Discord first | Phase 8 |
| Billing | Stripe Checkout/Portal, verified idempotent webhooks, server-side entitlements | Phase 9 |
| Hardening | Load/security testing, restore exercise, release artifacts and operating documentation | Phase 10 |

Manual process support initially provides status/logs for explicitly configured processes; lifecycle capabilities require safe local ownership. See [review decisions](review-decisions.md). Staff permissions and plan entitlements are separate checks. Plan labels FREE/PRO/GROWTH/NETWORK are product configuration, never authorization branches.

## User experience

Planned screens: landing, sign up/in, organization creation/dashboard, add server, installation wizard, overview, players, performance, logs, backups, alerts, settings, members, billing and audit log. Use clean typography and restrained layout, keyboard navigation, loading/empty/error states, text alongside status colors, and light/dark themes where practical. Do not fabricate statistics.

Overview shows server name/state/version, players/max, TPS/MSPT, CPU/RAM/disk/uptime, agent last seen and integration status. Distinguish stale, missing and zero measurements. Confirm disruptive actions. Show queued, sent, acknowledged, running and actual terminal results; no optimistic success.

Player analytics include current/recent players, first/last seen, sessions and playtime. Track enough data for future D1/D7/D30 retention without displaying unsupported conclusions. Do not collect player IPs, chat or private messages. Logs must respect that policy too.

## Operational requirements

Use PostgreSQL with migrations, normalized tenant-owned records, constraints and indexes. Redis is disposable. Retention defaults: raw metrics 7 days, five-minute aggregates 30 days, hourly aggregates 365 days (proposed); aggregate before deletion. Operational/audit history has a separate disclosed retention policy, never silent deletion. Organization erasure is explicit and auditable.

Only Caddy exposes production HTTP/HTTPS. PostgreSQL, Redis, Docker sockets, SSH, RCON and local agent APIs remain private. Environment-based configuration, non-root containers where feasible, health/readiness probes, persistent volumes, automatic restarts, structured redacted logs and correlation IDs are mandatory. Backups and restore procedures must be exercised before production.

## MVP acceptance scenario

The specification's “Phase 1 MVP” means the **product milestone after implementation phases 1–8**, distinct from repository-foundation Phase 1. A real user must be able to:

1. Register, verify identity and create an organization.
2. Add a server, install/enroll an agent and see it online.
3. See Minecraft state, host CPU/RAM/disk and current player count.
4. Start, stop and restart a supported runtime with accurate command status.
5. View recent operational events and an audit trail.
6. Configure Discord alerts and receive triggered/resolved notifications.
7. Trigger a consistent backup and see the resulting artifact metadata.

Acceptance includes a real Linux runtime plus a deterministic simulator E2E. Tenant A cannot read or command tenant B; VIEWER cannot restart; expired/reused enrollment and revoked agents fail; duplicate commands cannot repeat effects; malformed telemetry and unsupported commands fail; rate limits work. Phase 9 adds invalid-signature and duplicate Stripe webhook tests. CI must fail on required formatting/lint/types/tests/build failures.

## Delivery discipline

Work in reviewable phases. Before each: inspect, describe files/risks/acceptance. After each: run applicable checks, fix failures, document evidence and unresolved issues. Do not claim unrun behavior works. Stop after this architecture package for review. Later release readiness additionally requires Phase 10 hardening; the functional MVP alone is not a production-quality claim.
