# Security design

Status: proposed controls, not implemented or audited.

## Threat model

| Threat / boundary | Control | Verification |
| --- | --- | --- |
| Tenant crosses organization boundary | Membership authorization, scoped queries, composite tenant FKs, RLS | Two-tenant read/write/command/job tests |
| Stolen browser session or CSRF | HttpOnly Secure cookies, rotation/revocation, Origin and CSRF checks | Replay, logout, cross-origin and reset tests |
| Enrollment token intercepted/replayed | TLS, short lifetime, hashed token, atomic consumption, key binding | Concurrent enroll and expired/reused token tests |
| Fake or revoked agent | Device key proof, short-lived scoped credential, revocation checks | Challenge replay and live revocation tests |
| Compromised control plane requests shell/path access | Local operation allowlist and owner-defined bindings | Malformed parameter, target and traversal tests |
| Malicious plugin or telemetry | Local per-server secret, bounded input, tenant identity from credential | Spoofed server, oversized and invalid metric tests |
| Replayed commands / agent crash | Durable journal, deadlines, binding fencing, reconciliation | Crash at each transition and duplicate delivery tests |
| Webhook SSRF / secret leakage | Provider allowlist, public-address validation, redirect denial, encryption | Private IPv4/IPv6 and DNS rebinding tests |
| Flooding / resource exhaustion | Connection quotas, payload caps, bounded queues, throttles | Limits and recovery tests |
| Supply-chain or backup compromise | Locked dependencies, scans, least privilege, encrypted off-host backups | CI and restore exercises |

A compromised customer host can forge its own metrics and access local data; the platform cannot establish host integrity remotely. A compromised control plane could request permitted operations; local allowlists bound its power but cannot eliminate this risk. Docker access is effectively privileged and must be explicitly enabled by the owner.

## Human authentication

Use Argon2id through a maintained library with benchmarked cost, unique salts and password-length limits. Never implement cryptography. An identity-service boundary permits later OIDC adoption. Store unique normalized email and verification timestamp separately from profile data. Verification/reset/invite tokens are random, hashed, short-lived and single-use; generic responses prevent email enumeration. Reset revokes existing sessions and requires a new login.

Use random opaque browser access credentials with a 15-minute lifetime and rotating refresh credentials with a proposed 7-day idle/30-day absolute lifetime. Store hashes in PostgreSQL with a session-family ID; refresh rotation is atomic, and reuse revokes the family. Frontend coordinates concurrent refreshes. Logout, password change and account suspension revoke server-side sessions. Browser cookies are Secure, HttpOnly, SameSite=Lax and host-only; scope refresh cookie to its endpoint. Require CSRF token plus exact Origin checks for unsafe cookie-authenticated requests. No access tokens in browser local storage. Same-origin routing avoids broad CORS.

Rate-limit by account and source address for login/reset, by token/source for enrollment, and by user/org/agent for APIs and commands. Proposed starting limits: login 5 failures/minute/account plus 30/minute/source; reset 3/hour/account; enrollment 10/minute/source. Tune under measured legitimate use. Redis failure must not bypass protection. Recent reauthentication is required for ownership transfer, credential changes and destructive organization operations.

## Authorization

| Capability | OWNER | ADMIN | OPERATOR | VIEWER |
| --- | --- | --- | --- | --- |
| Read server health/player metrics | Yes | Yes | Yes | Yes |
| Read filtered logs/audit | Yes | Yes | Yes | No |
| Start/stop/restart; trigger backup | Yes | Yes | Yes | No |
| Configure servers, enroll/revoke agents, alerts and backup policy | Yes | Yes | No | No |
| Invite/manage non-owner members | Yes | Yes | No | No |
| Billing, ownership, delete organization | Yes | No | No | No |

ADMIN cannot create/remove/promote an OWNER; preserve at least one OWNER transactionally. Deny by default. API evaluates actor membership, resource tenant, action and current entitlements; the worker rechecks revocation/authorization before dispatch. Agent principals can only report for assigned bindings, never act as a user. Plugin credentials cannot invoke lifecycle actions. System jobs use explicit tenant scopes. UUID secrecy is not authorization.

## Enrollment and device identity

See [protocol](agent-protocol.md). An administrator creates a token scoped to one organization and initial server, expires in 10 minutes and can be consumed once under a row lock. Generate 256 random bits and store only a hash. Prefer `enroll --token-stdin` or hidden interactive input over positional tokens that leak into shell history/process listings.

Agent generates Ed25519 key material locally using standard libraries; private key permissions 0600 and directory 0700. Enrollment binds the public key through a server nonce proof; no private key leaves the host. The backend mints a 5-minute opaque connect credential after a fresh one-time challenge proof. Verify active identity at connect and at least every heartbeat, closing revoked sockets; revalidate before command dispatch. Rotate with proof from the active key and new key, short bounded overlap and audit. A lost key requires authorized re-enrollment and old credential revocation. Challenge formats and security tests must be frozen before Phase 3 implementation.

## Secret and command handling

Store browser/agent/enrollment bearer hashes, never reusable plaintext tokens. Encrypt notification secrets using an established AEAD library, versioned key IDs and associated tenant/resource context. Encryption keys are separate from the database and backed up separately. Production accepts mounted secret files or a secret manager; `.env.example` contains placeholders only. Redact headers, credentials, reset URLs and webhook paths from logs. Never send a stored webhook URL secret back to the browser.

Cloud commands contain typed parameters and opaque configured profile IDs, never shell strings, executable paths, service names or container IDs. Agent verifies negotiated operation, credential binding/generation, deadline, local permissions and concurrency locks. Run fixed executables with argument arrays or use local APIs; do not invoke a shell. systemd policy restricts exact unit names. Manual process control requires stable process identity to avoid PID reuse. Backup traversal must reject symlinks/escape paths and use owner-set roots. Retention cannot delete outside the backup root.

Only authenticated loopback plugin traffic is accepted; container networking needs an explicit isolated bridge and restricted port binding, never `0.0.0.0` by default. Per-server credentials map payloads to a binding. Queue network work off the game thread; snapshot game state using supported scheduling APIs.

## Tenant isolation, privacy and audit

Every tenant record carries `organization_id`; dependent rows use composite foreign keys `(organization_id, resource_id)`. All repository/domain lookups require tenant scope. Application authorization remains primary. Add FORCE RLS on tenant tables with transaction-local organization context; app role is neither table owner nor BYPASSRLS. Migration and maintenance identities are separate. Global identity lookup has narrowly scoped tables/functions. Test pooled connection context leakage, worker paths and aggregate reads.

Audit rows are append-only for runtime identities; record actor/action/resource/request/command IDs and safe metadata. Database administrators can still modify them; do not claim tamper-proof storage. Preserve history on resource soft deletion. Publish separate audit/operational retention rules and an explicit organization-erasure workflow including backup expiration.

Do not ingest player chat, IPs or private messages. Default to structured operational events. Raw console tail remains disabled until redaction/filtering is tested; arbitrary plugin log output may contain sensitive data, so generic regular-expression filtering is not a complete privacy guarantee. Security source IPs for human authentication have restricted access and proposed 30-day retention, distinct from forbidden player-IP collection.
