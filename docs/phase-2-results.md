# Phase 2 results

Status: in progress. Phase 1 baseline: `7af2d5d9252a8edb182c3386986c62bcf3b91ab3`.

## Scope

Phase 2 adds local user identity, opaque browser sessions, organizations,
memberships, owner/admin/member RBAC, and backend-enforced tenant isolation.
It does not add server-management functionality.

## Data model

Migration `0002_identity_organizations` creates UUID-keyed users,
organizations, and memberships. Email identifiers are normalized to lowercase;
memberships are unique per user/organization and roles are database-constrained
to `owner`, `admin`, or `member`. The next checkpoint adds authentication,
authorization, and RLS policies that consume this schema.

Migration `0003_browser_sessions` adds hashed, revocable, expiring opaque
browser-session records. Plain session credentials will never be stored.
