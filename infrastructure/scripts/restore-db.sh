#!/bin/sh
# Restore only into a new named database, never overwrite platform.
set -eu
: "${COMPOSE_FILE:=compose.production.yaml}"
archive=${1:?Usage: restore-db.sh archive.dump new_database}
destination=${2:?Specify a NEW disposable/recovery database}
case "$destination" in
  restore_[a-zA-Z0-9_]*) ;;
  *) echo 'Destination must begin restore_ and contain only letters, digits or underscores.' >&2; exit 2 ;;
esac
case "$destination" in *[!a-zA-Z0-9_]*) exit 2 ;; esac
docker compose -f "$COMPOSE_FILE" exec -T postgres createdb -U postgres -O platform_migrator "$destination"
docker compose -f "$COMPOSE_FILE" exec -T postgres pg_restore -U postgres --exit-on-error --single-transaction -d "$destination" < "$archive"
printf 'Restored into %s; validate before any cutover.\n' "$destination"
