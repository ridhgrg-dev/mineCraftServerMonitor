#!/bin/sh
set -eu
umask 077
: "${COMPOSE_FILE:=compose.production.yaml}"
: "${BACKUP_DIR:=backups}"
mkdir -p "$BACKUP_DIR"
archive="$BACKUP_DIR/platform-$(date -u +%Y%m%dT%H%M%SZ)-$$.dump"
trap 'rm -f "$archive.partial"' EXIT HUP INT TERM
docker compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U postgres -d platform --format=custom > "$archive.partial"
mv "$archive.partial" "$archive"
printf '%s\n' "$archive"
