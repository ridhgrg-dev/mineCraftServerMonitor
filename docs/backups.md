# PostgreSQL backup and restore

Scope: control-plane database only. Minecraft world backups are a later feature. These scripts require Docker. The Phase 1 disposable rehearsal passed, including sentinel data and migration-version verification in a separate restored database.

## Backup

```sh
COMPOSE_FILE=compose.production.yaml infrastructure/scripts/backup-db.sh
```

This creates a custom-format `pg_dump` archive under `backups/` with private permissions, a UTC filename and temporary-file-to-final rename. It exits on dump failure. Schedule it externally only after validating the restore procedure. Encrypt and copy archives off-host, verify transfer checksums and maintain a documented retention policy. Database archives do not contain cluster login passwords; store the bootstrap/role recovery credentials separately. Treat archives as sensitive even in Phase 1.

## Restore rehearsal or recovery

Provision compatible PostgreSQL and both platform roles through the bootstrap procedure first. Restore only into a **new** database whose name begins with `restore_`:

```sh
COMPOSE_FILE=compose.production.yaml infrastructure/scripts/restore-db.sh backups/<archive>.dump restore_rehearsal
# Inspect migration revision:
docker compose -f compose.production.yaml exec postgres psql -U postgres -d restore_rehearsal -c 'SELECT version_num FROM public.alembic_version'
```

`createdb` refuses an existing destination; `pg_restore --exit-on-error --single-transaction` prevents a partial successful restore. The script never overwrites the live `platform` database. A failed destination remains available for diagnosis; remove it explicitly only after verifying it is disposable.

Validate restored schema, role grants, RLS context behavior and relevant application data. Do not automatically cut production over. For actual disaster recovery, stop writers, prepare a reviewed new runtime/migration URL pointing to the validated restore database, deploy and verify readiness before admitting traffic. Keep the original archive and failed environment until recovery is confirmed.

## Automated disposable check

`infrastructure/scripts/verify-compose.sh` uses a unique Compose project, generated credentials and its own volumes. It migrates an empty database, inserts a test-only sentinel, dumps it, restores into a separate database, verifies both sentinel and Alembic revision and then deletes that test project's volumes. Test-only tables never appear in application migrations.

The nominal control-plane RPO of 24 hours and RTO of 4 hours are proposals, not achieved guarantees. Record archive size, elapsed restore time and verification evidence before claiming those objectives.
