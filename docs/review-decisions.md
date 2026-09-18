# Architecture review and specification adjustments

Status: proposed; all nine ADRs await review. The requested architecture artifacts are complete, but no runtime security or compatibility claim has been validated by application tests.

| Decision | Recommended resolution | Why / consequence |
| --- | --- | --- |
| Two meanings of Phase 1 | Call the 14-step product outcome the “functional MVP”; reserve Phase 1 for foundation | MVP spans implementation phases 1–8; release readiness also needs hardening |
| Host versus server identity | One agent per organization-owned host, multiple explicit server bindings | Avoid duplicate host metrics and multiple privileged daemons; support binding generations |
| Agent authentication | Standard TLS plus Ed25519 device challenge proof and short-lived opaque scoped credentials | Meets device-owned key requirement without deploying a customer certificate authority; freeze protocol fixtures before Phase 3 |
| Tenant defense | Application RBAC plus composite FKs and FORCE RLS from first tenant tables | Requires transaction-local context and separate migration/runtime roles; adds test burden but protects missed filters |
| Command delivery | At-least-once delivery with durable local journal; reconcile ambiguous effects | Exactly-once external effects cannot be guaranteed across crashes; never auto-repeat uncertain restart |
| Backup consistency | Initially require stopped runtime for backups; operator explicitly stops first | Live file copies can corrupt worlds. Defer online snapshots until a tested flush/freeze/snapshot adapter exists; do not silently stop a live server |
| Manual processes | Status/logs first; lifecycle only for a locally owned configured supervisor | Arbitrary PIDs and cloud-supplied launch commands are unsafe; Docker/systemd are initial control targets |
| Console privacy | Structured operational events by default; raw log tails gated on a reviewed local filter | Minecraft/plugin output can include chat and player IPs, conflicting with privacy requirements |
| Paper compatibility | Start with current documented Paper 26.x/Java 25; evaluate older Java 21 line separately if needed | Do not assume the historical Java 21 requirement applies to current Paper |
| Latest versus supported | Prefer supported stable/LTS runtime lines, exact patch pins at implementation | Latest Current Node is not necessarily the production choice; web docs alone cannot prove mutual package compatibility |
| Redis role/license | Use Redis only for ephemeral coordination; verify selected distribution/license before lock | Durable work remains PostgreSQL-backed; licensing choice must be recorded before shipping |
| Single-host capacity | EliteDesk is initial deployment, not a 5,000-server capacity commitment | Partition/aggregate from the outset, benchmark and scale before reaching target |
| Recovery policy | Provisional control-plane RPO 24h/RTO 4h; independent world backup policy | Must be accepted and demonstrated by restore rehearsal before launch |
| Billing before Stripe | Explicit configured free entitlements initially; Stripe delivery in Phase 9 | Authorization remains entitlement-based without inventing paid subscriptions |

## Backup and alert implementation constraints

Backup profiles are installed locally by the owner and referenced by opaque IDs. Check free space with a safety reserve, serialize per-server backup/lifecycle work, reject unsafe paths and symlinks, write a temporary artifact, checksum and atomically finalize it. Keep failure metadata and never prune the last known good artifact solely to make room for a failing backup. Retention deletes only validated artifacts under the configured root. Do not restart a server automatically after a backup unless a separate explicit workflow has been approved. Future S3-compatible adapters upload directly from the agent.

Alert rules use persisted pending/firing/resolved state, threshold duration, hysteresis where appropriate, cooldown and unique transition deliveries. Offline detection uses receipt time. Distinguish agent offline from confirmed runtime offline; do not send duplicate dependent alerts for every missing metric. Discord delivery retries on rate limits/transient failures with deduplication and a bounded retry budget. Keep provider secrets encrypted and return only a masked display value.

## Review gate

Review the recommendations above and [ADRs](adr/README.md), especially identity, RLS, crash ambiguity, backup consistency and supported Paper versions. Accept or revise them before Phase 1 implementation. This stop is explicitly required by the initial prompt: “Do not implement Phase 1 until the architecture has been reviewed.”

## Validation scope

This package is documentation only. Local relative links, required artifact presence, Markdown whitespace/fences and ADR completeness are checked mechanically. Mermaid sources receive textual review; rendered diagrams and application format/lint/type/test/build checks require tooling that is not yet present. No application, deployment or performance behavior is claimed to work.
