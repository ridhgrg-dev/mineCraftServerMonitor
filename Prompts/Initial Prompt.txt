You are the principal software architect and senior engineering team responsible
for building a production-quality commercial SaaS platform from an empty Git
repository.

PROJECT CODENAME
================
MineOps

The name is temporary. Do not tightly couple branding to the implementation.

PRODUCT VISION
==============
Build a professional Minecraft server management SaaS for independent Minecraft
server owners, communities, and multi-server networks.

This is NOT a Minecraft cheating bot, player automation system, hacked client,
or gameplay exploit.

It is legitimate infrastructure and management software for server owners.

The product should eventually allow a Minecraft server owner to:

- connect one or more Minecraft servers to a cloud/self-hosted dashboard
- see whether each server is online
- see players currently online
- monitor TPS, MSPT, CPU, RAM, uptime and storage
- see player joins and leaves
- start, stop and restart servers
- see console/log events
- receive alerts
- configure scheduled backups
- review historical analytics
- analyze player retention
- manage multiple servers
- invite staff with different permissions
- receive Discord notifications
- later track monetization/revenue
- later receive AI-generated operational insights

We are initially developing on:
- Intel MacBook Pro 2018
- Linux HP EliteDesk mini
- eventual AWS deployment

Therefore everything must support:
- macOS development
- Linux production
- Docker-based deployment
- ARM/x86 differences where practical
- migration from an EliteDesk to AWS without rewriting the application

Do not assume Kubernetes.
Do not introduce Kubernetes for the MVP.

PRIMARY DESIGN PRINCIPLE
========================
Separate the platform into three components:

1. CONTROL PLANE
   Hosted SaaS application.

2. HOST AGENT
   Small daemon installed on the machine running the Minecraft server.

3. PAPER PLUGIN
   Minecraft Paper plugin providing game-specific telemetry and events.

The architecture must support replacing or extending Minecraft with other game
server adapters in the future.

Examples:
- Minecraft
- ARK
- Rust
- Palworld
- other dedicated servers

Minecraft must therefore be an adapter/integration, not deeply hard-coded into
the entire platform.

SECURITY MODEL
==============
Security is a first-class requirement.

Never expose a customer's RCON port, Docker socket, SSH port, database,
filesystem, or control API directly to the public Internet.

The Host Agent must initiate an OUTBOUND authenticated TLS connection to the
Control Plane.

Preferred command flow:

Web dashboard
    |
    v
Control Plane
    |
 authenticated command
    v
Outbound agent connection
    |
    v
Host Agent
    |
    v
Minecraft process / container / systemd service

Do NOT design the platform so that the cloud backend makes unsolicited inbound
connections to customer machines.

The Host Agent must NEVER accept arbitrary shell commands from the cloud.

Implement an explicit allowlist of supported operations such as:

- server.start
- server.stop
- server.restart
- server.status
- server.backup
- server.logs.tail

Each operation must:
- use typed structured parameters
- validate inputs
- enforce authorization
- create an audit record
- have a timeout
- return structured success/failure results

Do not provide a generic:
execute_shell("...")
endpoint.

ARCHITECTURE
============

Use a monorepo.

Suggested structure:

/
  apps/
    web/
    api/

  agents/
    host-agent/

  integrations/
    minecraft-paper/

  packages/
    shared/
    api-client/
    schemas/

  infrastructure/
    docker/
    caddy/
    scripts/

  docs/

  .github/
    workflows/

Choose sensible naming where needed.

TECHNOLOGY STACK
================

Frontend:
- Next.js
- TypeScript
- React
- Tailwind CSS
- accessible component system
- responsive UI
- strict TypeScript
- server/client boundaries used correctly

Backend:
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

Database:
- PostgreSQL

Cache / ephemeral state:
- Redis

Host Agent:
- Go

Minecraft integration:
- Java or Kotlin
- Paper API
- Gradle

Infrastructure:
- Docker
- Docker Compose
- Caddy for HTTPS/reverse proxy
- PostgreSQL
- Redis

Testing:
- pytest
- frontend unit/component testing
- Playwright for end-to-end testing
- Go tests
- Java/Kotlin tests

CI/CD:
- GitHub Actions

API:
- REST for normal request/response operations
- WebSocket or other appropriate persistent channel for connected Host Agents
- OpenAPI generated and maintained

Do not blindly pin versions from this prompt.
Before implementation, verify the latest stable supported releases from official
documentation and choose mutually compatible versions.

Document all selected versions.

Avoid experimental dependencies unless there is a compelling documented reason.

TENANCY MODEL
=============

The product is multi-tenant.

Core hierarchy:

User
Organization
OrganizationMember
Server
ServerAgent
MinecraftServer
Player
PlayerSession
Metric
Alert
AlertRule
Backup
Command
CommandExecution
AuditEvent
Subscription
Entitlement

A user may belong to multiple organizations.

An organization may own multiple servers.

Organization roles initially:

OWNER
ADMIN
OPERATOR
VIEWER

Permissions must be enforced server-side.

Never trust frontend authorization.

Build a reusable authorization layer.

DATABASE
========

Use PostgreSQL.

Use UUIDs for externally exposed resource identifiers.

Every tenant-owned record must clearly identify its organization.

Prevent cross-tenant access by design.

Consider PostgreSQL Row-Level Security where it provides meaningful
defense-in-depth, but do not rely on RLS instead of application authorization.

Use:
- foreign keys
- indexes
- unique constraints
- check constraints
- timestamps
- migrations

Do not use JSON blobs for data that belongs in normalized relational tables.

JSONB is acceptable where schemaless metadata is genuinely appropriate.

Never silently delete operational history.

AUTHENTICATION
==============

Implement production-quality authentication.

Requirements:
- secure password hashing using Argon2id or an equivalently modern scheme
- email verification architecture
- password reset flow
- secure cookies where applicable
- CSRF protections where applicable
- short-lived access credentials
- refresh/session rotation
- revocation
- logout
- brute-force protection
- rate limiting

Do not invent custom cryptography.

Structure authentication so an external identity provider could replace it
later without redesigning the entire application.

AGENT ENROLLMENT
================

Server onboarding should work approximately like this:

1. Owner creates a server in the dashboard.
2. Dashboard generates a short-lived enrollment token.
3. User installs the Host Agent.
4. User runs:

   mineops-agent enroll <token>

5. Agent generates its own device identity/key.
6. Backend validates the one-time enrollment token.
7. Backend associates device with organization/server.
8. Enrollment token becomes unusable.
9. Agent receives only what it needs to operate.
10. Long-lived secrets are never displayed again.

Do not store reusable plaintext enrollment tokens.

Agent credentials must support:
- rotation
- revocation
- re-enrollment

AGENT COMMUNICATION
===================

The Host Agent establishes an outbound secure connection.

Implement:

- heartbeats
- reconnect with exponential backoff and jitter
- connection status
- command acknowledgement
- command result reporting
- idempotency
- command timeout
- unique command IDs
- duplicate command protection
- graceful shutdown
- protocol version negotiation

A temporary network outage must not crash the agent.

The platform should show:

Online
Offline
Degraded
Last seen

Do not mark a server offline simply because one telemetry message was delayed.

HOST AGENT
==========

Implement the agent as a small Go binary.

Responsibilities:

- registration/enrollment
- authenticated connection
- host telemetry
- Minecraft process/container detection
- server status
- start
- stop
- restart
- log streaming/tailing
- backups
- Paper plugin communication where available

The agent should support adapters.

Initial runtime adapters:

1. Docker-managed Minecraft server
2. systemd-managed Minecraft server
3. manually configured process

Do not directly expose the Docker socket to the Control Plane.

The local Host Agent may interact with Docker if configured by the owner.

Use least privilege.

Provide an installation path for Linux first.

Future Windows support should remain architecturally possible.

MINECRAFT PAPER PLUGIN
======================

Build a Paper plugin.

Do not depend on Minecraft internals/NMS unless absolutely unavoidable.

Use documented Paper APIs.

Collect:

- server version
- plugin version
- online player count
- maximum players
- player join
- player quit
- player UUID
- player display/name information where appropriate
- TPS
- MSPT if supported by the API
- world identifiers
- server tick/performance information available through supported APIs

Do not collect private chat messages by default.

Do not collect unnecessary personal information.

The plugin should communicate locally with the Host Agent rather than opening a
public Internet-facing server.

Plugin -> localhost Agent -> Control Plane

Authentication must exist between plugin and local agent.

If the plugin is not installed, the Host Agent should still provide host-level
monitoring.

The UI should indicate:

Agent connected
Minecraft detected
Paper integration installed/not installed

REAL-TIME TELEMETRY
===================

Collect at reasonable intervals.

Do not flood the backend.

Examples:

Host metrics:
30-60 second intervals

Minecraft health:
10-30 second intervals

Join/quit:
event-driven

Use aggregation for long-term metrics.

Do not store one row every second forever.

Design retention:

high-resolution recent telemetry
hourly aggregates
daily aggregates

Create a cleanup/aggregation strategy.

INITIAL DASHBOARD
=================

Create a polished SaaS interface.

Primary screens:

1. Marketing landing page
2. Sign up
3. Sign in
4. Create organization
5. Organization dashboard
6. Add server
7. Agent installation wizard
8. Server overview
9. Players
10. Performance
11. Logs
12. Backups
13. Alerts
14. Settings
15. Members
16. Billing
17. Audit log

SERVER OVERVIEW
===============

Show at minimum:

Server name
Online/offline state
Minecraft version
Current players
Maximum players
TPS
MSPT
CPU
RAM
Disk
Uptime
Agent last seen
Minecraft integration status

Actions:

Start
Stop
Restart

Dangerous actions must require confirmation.

The UI should immediately show that a command has been requested.

Never fake success.

Display:

Queued
Sent
Acknowledged
Running
Succeeded
Failed
Timed out

PLAYERS
=======

Track player sessions.

Provide:

current players
recent players
first seen
last seen
total sessions
total playtime
average session duration

Build data structures now that can later support:

D1 retention
D7 retention
D30 retention
new vs returning players

Do not claim retention metrics until enough data exists.

BACKUPS
=======

Implement a safe backup architecture.

Initial version:
- owner configures destination/path
- agent creates backup
- use safe filenames
- detect insufficient disk space
- prevent overlapping backups
- track start/end/status/size
- enforce retention policy

Future:
- S3-compatible storage

Design interfaces now so local backup storage can later be replaced with:
AWS S3
Cloudflare R2
Backblaze B2
other S3-compatible providers

Do not upload backups to the Control Plane API itself.

ALERTING
========

Initial alert rules:

Server offline
Agent offline
High CPU
High RAM
Low disk space
Low TPS
High MSPT
Backup failed

Architecture must support:

email
Discord webhook

later:
Slack
SMS
push

Alerts require:
- thresholds
- duration
- cooldown
- deduplication
- resolved state

Avoid alert spam.

DISCORD
=======

Implement Discord webhook notifications first.

Events:

server offline
server recovered
backup failed
high resource usage

Secrets must be encrypted at rest or stored using an appropriate secrets
mechanism.

Never send a webhook secret back to the browser after it has been stored.

BILLING
=======

Use Stripe Billing.

Do not store credit card numbers.

Implement:

Stripe Checkout
Stripe Customer Portal
subscription webhooks
subscription status
plan entitlements
billing history link

Example initial plans:

FREE
- 1 server
- basic status
- short data retention

PRO
- more retention
- alerts
- backups
- advanced analytics

GROWTH
- multiple servers
- additional members
- longer analytics
- advanced automation

NETWORK
- many servers
- organization features
- API access later

DO NOT hard-code feature checks such as:

if plan == "pro"

Instead create entitlement-based authorization.

Examples:

servers.max
history.days
alerts.enabled
backups.enabled
members.max
advanced_analytics.enabled

Stripe webhooks are authoritative for billing state.

Verify webhook signatures.

Make webhook processing idempotent.

Never grant paid access based solely on frontend redirect success.

OBSERVABILITY
=============

Use structured JSON logging.

Every request should have a request/correlation ID.

Every agent command should have a command ID.

Do not log:
passwords
tokens
authorization headers
private keys
Stripe secrets
webhook secrets

Implement:

health endpoint
readiness endpoint
database health
Redis health
agent connection metrics

Architecture should be compatible with:
Prometheus
OpenTelemetry
Sentry

These integrations may initially be optional.

AUDIT LOGGING
=============

Create immutable-style audit records for important operations:

login
failed login where appropriate
server created
server deleted
agent enrolled
agent revoked
server started
server stopped
server restarted
member invited
role changed
billing changes
backup triggered
settings changed

Record:

organization
actor
action
resource
timestamp
IP where appropriate
metadata

Avoid sensitive data.

API DESIGN
==========

Use clean resource-oriented routes.

Version public APIs:

/api/v1/...

Create consistent errors:

{
  "error": {
    "code": "...",
    "message": "...",
    "request_id": "..."
  }
}

Validate all input.

Use pagination.

Do not expose database models directly.

Separate:
database models
domain models
API schemas

Do not allow mass assignment.

RATE LIMITING
=============

Implement sensible rate limiting for:

authentication
password reset
agent enrollment
API
command execution

Protect expensive endpoints.

Do not make rate limits so restrictive that normal dashboard use breaks.

FRONTEND QUALITY
================

The product should look like professional infrastructure SaaS.

Do NOT create:
- giant gradients
- gimmicky animations
- fake statistics
- excessive cards
- toy-looking UI

Prefer:
- clean typography
- restrained visual hierarchy
- responsive layouts
- accessible controls
- keyboard navigation
- clear empty states
- loading states
- error states
- skeleton states where useful

Support dark and light modes if practical.

Use WCAG-minded accessibility.

Never convey status using color alone.

COMMAND UX
==========

When Restart is clicked:

1. ask for confirmation
2. POST command
3. show queued
4. update as agent receives it
5. show running
6. show actual success/failure

Do not optimistically display "Restarted successfully" before agent confirmation.

BACKGROUND PROCESSING
=====================

Use a background worker where needed.

Potential jobs:

metrics aggregation
alert evaluation
email
billing event processing
cleanup
retention jobs

Avoid doing expensive jobs in HTTP request handlers.

FILE AND SECRET MANAGEMENT
==========================

Provide:

.env.example

Never commit:
.env
secrets
private keys
database passwords

Production secrets come from environment variables/secrets management.

Use separate settings for:
development
test
production

LOCAL DEVELOPMENT
=================

A new developer should be able to:

git clone
copy .env.example
run one or two commands
open the application

Aim for:

docker compose up

Provide seed/demo data.

Provide a documented demo server/agent mode so frontend developers can test
without running Minecraft.

MACBOOK DEVELOPMENT
===================

The project must run on a 2018 Intel MacBook Pro for development.

Avoid requiring huge local infrastructure.

Minecraft itself should not need to run for normal dashboard/backend
development.

Create simulators/mocks for agent telemetry.

ELITEDESK DEPLOYMENT
====================

Provide a production Docker Compose configuration optimized for a single Linux
host.

Include:

web
api
worker
postgres
redis
caddy

Do not expose PostgreSQL or Redis publicly.

Only Caddy should expose necessary HTTP/HTTPS ports.

Containers should:

restart automatically
have health checks
use persistent volumes
use production builds
run as non-root where feasible

Provide:

compose.yaml
compose.production.yaml

Create a documented backup procedure for PostgreSQL.

Create a documented restore procedure.

Caddy should automatically manage HTTPS when a domain is configured.

AWS MIGRATION
=============

Design deployment so moving from EliteDesk to AWS does not require application
changes.

Configuration must come from environment.

Storage should use interfaces/adapters.

Do not use host-specific absolute paths in application logic.

Eventually we may use:

AWS EC2/Lightsail
AWS RDS PostgreSQL
AWS ElastiCache or managed Redis
AWS S3

But the MVP must not require these.

TESTING REQUIREMENTS
====================

Production quality means tests are mandatory.

Backend:
- domain unit tests
- authorization tests
- tenant isolation tests
- API tests
- billing webhook tests
- enrollment tests
- command lifecycle tests

Agent:
- enrollment tests
- reconnection tests
- duplicate command tests
- adapter tests
- command allowlist tests

Minecraft plugin:
- event conversion tests
- serialization tests
- configuration tests

Frontend:
- critical component tests

End to end:
- signup/login
- organization creation
- add server
- simulated agent enrollment
- server appears online
- restart command
- command succeeds
- invite member
- permissions enforced

Use Playwright for browser E2E tests.

SECURITY TESTS
==============

Explicitly test:

User from Organization A cannot view Organization B.
User from Organization A cannot command Organization B's server.
VIEWER cannot restart servers.
Revoked agent cannot reconnect.
Expired enrollment token cannot enroll.
Enrollment token cannot be reused.
Stripe webhook with invalid signature fails.
Duplicate Stripe webhook is idempotent.
Duplicate agent command does not execute twice.
Malformed telemetry is rejected.
Agent cannot execute unsupported command.
Rate limits work.

CI
==

GitHub Actions must run:

formatting
lint
type checking
unit tests
integration tests
frontend build
backend tests
Go tests
plugin tests
container image builds
dependency/security checks where reasonable

A pull request with failing tests must fail CI.

DEPENDENCIES
============

Keep dependency count reasonable.

Before adding a dependency ask:

1. Is it actively maintained?
2. Do we actually need it?
3. Can the standard library/framework already do it?
4. Does it materially increase attack surface?
5. What is its license?

Document significant dependencies.

DOCUMENTATION
=============

Create high-quality documentation.

At minimum:

README.md
docs/architecture.md
docs/development.md
docs/deployment.md
docs/security.md
docs/agent-protocol.md
docs/minecraft-plugin.md
docs/database.md
docs/backups.md
docs/disaster-recovery.md
docs/billing.md

README should include:

what the project does
architecture diagram
requirements
quick start
development commands
test commands
deployment overview

Include Mermaid architecture diagrams.

CODE QUALITY
============

Use clear domain boundaries.

Avoid:
- enormous files
- god classes
- circular dependencies
- duplicate logic
- hidden global state
- magic strings
- untyped dictionaries everywhere
- premature abstractions

Prefer:
- typed interfaces
- dependency injection where useful
- cohesive modules
- explicit domain services
- repositories only where they meaningfully simplify persistence
- small understandable functions

Do not add abstraction merely because "enterprise architecture" sounds good.

ERROR HANDLING
==============

Never silently swallow exceptions.

Errors should:
- have useful context
- avoid leaking secrets
- be logged appropriately
- return safe client messages

Agent failures should provide actionable reasons.

For example:

Minecraft executable not found
Insufficient permission
Server did not stop before timeout
Backup failed: insufficient disk space

Do not return raw stack traces to customers.

PRIVACY
=======

Collect the minimum data necessary.

Do not collect:
chat messages
IP addresses of Minecraft players
private messages

unless a clearly justified future feature explicitly requires it.

Minecraft player UUID and name are sufficient for initial player analytics.

Provide a path to deleting an organization's data.

PERFORMANCE
===========

Design for an initial target of:

1,000 organizations
5,000 managed servers
many simultaneously connected agents

This does NOT mean premature microservices.

Start with a modular monolith backend.

Design boundaries so high-volume telemetry can be separated later if required.

Do not introduce Kafka at this stage.

Metrics ingestion should:
- batch where possible
- avoid one HTTP request per metric
- use bulk inserts
- aggregate historical data

DATA RETENTION
==============

Implement configurable retention.

Example:

raw metrics: 7 days
5-minute aggregates: 30 days
hourly aggregates: longer-term

Do not permanently retain unlimited high-resolution telemetry.

AI FEATURES
===========

AI is NOT required in Phase 1.

Do not put LLM calls into critical server control paths.

Create architectural room for future features such as:

"Why was my server lagging last night?"
"Summarize this crash."
"Which plugin may be causing performance degradation?"
"Why are players leaving?"
"Summarize this week's operational issues."

AI recommendations must never automatically execute destructive server
operations without explicit authorization.

MVP DEFINITION
==============

Phase 1 is complete only when a real user can:

1. register
2. create an organization
3. add a Minecraft server
4. install/enroll an agent
5. see the agent online
6. see Minecraft status
7. see CPU/RAM/disk
8. see current player count
9. issue Start/Stop/Restart
10. receive accurate command status
11. view recent operational events
12. configure a Discord alert
13. trigger a backup
14. view an audit trail

Do not begin advanced AI features before this works reliably.

IMPLEMENTATION PHASES
=====================

PHASE 0 — Architecture
- inspect repository
- research current stable dependencies
- produce ADRs
- create architecture diagrams
- finalize schemas
- establish security model
- establish API conventions

PHASE 1 — Repository foundation
- monorepo
- tooling
- Docker Compose
- PostgreSQL
- Redis
- FastAPI
- Next.js
- migrations
- test infrastructure
- CI

PHASE 2 — Identity and organizations
- authentication
- organizations
- memberships
- RBAC
- tenant isolation

PHASE 3 — Server registration
- server CRUD
- agent enrollment tokens
- agent identity
- secure handshake

PHASE 4 — Host Agent
- Go agent
- heartbeat
- system metrics
- reconnect
- command protocol
- simulated runtime adapter

PHASE 5 — Dashboard
- overview
- servers
- server details
- telemetry
- online/offline state

PHASE 6 — Minecraft integration
- Paper plugin
- player events
- performance telemetry
- plugin-agent local connection

PHASE 7 — Server control
- Docker adapter
- systemd adapter
- Start/Stop/Restart
- command lifecycle
- audit logging

PHASE 8 — Backups and alerts
- backups
- retention
- Discord
- rule engine

PHASE 9 — Billing
- Stripe
- subscriptions
- entitlements
- billing portal
- webhook handling

PHASE 10 — Production hardening
- load testing
- security review
- performance profiling
- disaster recovery test
- backup/restore test
- documentation
- release pipeline

CODEX WORKING RULES
===================

Do not attempt to build the entire product in one giant unreviewable change.

Work phase by phase.

At the beginning of every phase:

1. inspect existing code
2. explain the proposed implementation
3. identify affected files
4. identify risks
5. define acceptance criteria

Then implement.

At the end of every phase:

1. run formatting
2. run lint
3. run type checks
4. run tests
5. run builds
6. fix failures
7. update documentation
8. provide a concise summary
9. list any unresolved issues
10. stop for review if a significant architectural decision is needed

Never claim something works without running the relevant test or build.

Do not leave fake implementations such as:

TODO
return true
mock success
hard-coded users
hard-coded subscriptions

in production paths.

Mocks are allowed only in clearly identified test/demo code.

When information is uncertain, consult official project documentation rather
than guessing.

Prefer official documentation over random blog posts.

Do not automatically rewrite a working subsystem merely because another
approach looks more fashionable.

BACKWARD COMPATIBILITY
======================

The Agent protocol must be versioned.

Backend deployments must tolerate a reasonable transition period where agents
may be one release behind.

Do not require every customer's agent to upgrade at exactly the same second as
the server.

UPDATES
=======

Eventually support secure agent updates.

Do not implement insecure arbitrary binary download/execution.

Release artifacts must eventually support:
- checksums
- signatures
- version metadata

The user must be able to see installed agent/plugin version from dashboard.

AUDITABLE BUSINESS LOGIC
========================

Subscription/entitlement decisions must happen server-side and be testable.

Important operations should produce an audit trail.

No destructive action should depend solely on frontend state.

DEFINITION OF PRODUCTION QUALITY
================================

Production quality for this project means:

- secure defaults
- real authorization
- tenant isolation
- migrations
- tests
- CI
- backups
- restore procedure
- observability
- documented deployment
- responsive UI
- accessible UX
- graceful errors
- idempotency
- rate limiting
- no secret leakage
- no fake success states
- no public database
- no public Redis
- no exposed customer RCON
- no generic remote shell
- reproducible builds
- documented architecture

FIRST TASK
==========

Do NOT immediately generate the entire application.

Start by doing the following:

1. Create docs/product-requirements.md summarizing this specification.

2. Create docs/architecture.md containing:
   - system architecture
   - trust boundaries
   - component responsibilities
   - data flow
   - agent communication model
   - deployment architecture
   - Mermaid diagrams

3. Create docs/security.md containing:
   - threat model
   - authentication model
   - authorization model
   - agent enrollment security
   - secret management
   - command execution security
   - tenant isolation strategy

4. Create docs/adr/ with initial Architecture Decision Records for:
   - monorepo structure
   - backend stack
   - frontend stack
   - Host Agent language
   - Paper plugin architecture
   - PostgreSQL
   - Redis
   - outbound agent connection
   - Docker Compose deployment

5. Propose the initial database schema.

6. Propose the agent protocol.

7. Produce the planned repository directory tree.

8. Produce the Phase 1 implementation plan.

9. Identify anything in this specification that should be changed before
   implementation and explain why.

STOP after completing those architecture/design artifacts.

Do not implement Phase 1 until the architecture has been reviewed.
