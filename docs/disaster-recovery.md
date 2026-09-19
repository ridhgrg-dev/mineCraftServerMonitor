# Disaster recovery foundation

Follow [backup and restore](backups.md). Recover secrets/role credentials separately, provision a compatible PostgreSQL service, restore into a new database, verify schema/data/access, then switch application configuration during a controlled outage. Revoke exposed credentials if the incident involved compromise. Recreate Redis as disposable state; it is never a backup source or authority for accepted work.

Caddy certificate storage can be restored from its persistent volume or certificates reissued subject to issuer limits. Preserve deployment configuration and version/digest inventory. Do not infer world-backup recovery from successful control-plane recovery. Phase 1 exercised database restore in a disposable Docker environment. That rehearsal does not establish production recovery time or a complete host-failure drill.
