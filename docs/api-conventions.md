# API conventions

Status: proposed. REST prefix `/api/v1`; JSON request/response schemas are separate from SQLAlchemy models. Pydantic schemas produce OpenAPI and the generated TypeScript client. Versioned agent JSON Schemas live separately under `packages/schemas`.

Use UUID resource IDs, RFC3339 UTC timestamps, explicit units, nullable unavailable metrics and cursor pagination ordered by `(created_at, id)` (default 50, max 200). Validate allowlisted fields and reject extra mutation fields. Tenant scope comes from an authenticated membership plus the requested organization, never unchecked payload data.

Representative routes:

| Route | Purpose |
| --- | --- |
| `POST /auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout` | Human sessions |
| `POST /auth/verify-email`, `/auth/password-reset/request`, `/auth/password-reset/confirm` | Recovery/verification |
| `GET/POST /organizations` | Membership-scoped discovery/create |
| `GET/POST /organizations/{org}/servers` | Tenant server collection |
| `GET/PATCH/DELETE /organizations/{org}/servers/{server}` | Server read/update/soft delete |
| `POST /organizations/{org}/servers/{server}/enrollment-tokens` | One-time onboarding |
| `POST /organizations/{org}/servers/{server}/commands` | Request typed operation |
| `GET /organizations/{org}/commands/{command}` | Persisted lifecycle |
| `GET /organizations/{org}/servers/{server}/metrics` | Bounded time range/resolution |
| `GET /organizations/{org}/audit-events` | Authorized audit read |
| `POST /agent-enrollments`, `/agent-auth/challenges`, `/agent-auth/tokens` | Device bootstrap and authentication |
| `GET /agents/connect` (WebSocket upgrade) | Agent-established channel |
| `POST /webhooks/stripe` | Raw-body signature verified webhook |

Creation returns 201; queued commands return 202 plus a Location header. Missing or inaccessible tenant resources return the same 404; authenticated role denial within a known tenant returns 403. Use 401 for invalid credentials, 409 for state/idempotency conflicts, 422 for validation, 429 with Retry-After for throttling and 503 for unavailable dependencies.

```json
{"error":{"code":"command.not_supported","message":"This server does not support restart.","request_id":"2f809e76-ea08-4f5a-91db-d65432cdfdbb"}}
```

Require `Idempotency-Key` for commands and other costly retriable mutations. Uniqueness is `(organization_id, actor_id, operation_scope, key)` with a normalized request hash; same key/body returns the original response, different body returns 409. Retain command idempotency at least as long as its command history. Use optimistic resource versions/If-Match for concurrent configuration updates.

Every request gets a validated or generated correlation ID. Never return stack traces. Health liveness does not require dependencies; readiness checks PostgreSQL and required Redis access with deadlines and no secret details. Stripe webhook authentication is separate from browser CSRF; verify exact raw bytes and persist a unique provider event before acknowledging.
