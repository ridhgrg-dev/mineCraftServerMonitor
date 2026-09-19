#!/bin/sh
set -eu
: "${APP_DB_PASSWORD:?required}"
: "${MIGRATION_DB_PASSWORD:?required}"
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  --set=app_password="$APP_DB_PASSWORD" --set=migration_password="$MIGRATION_DB_PASSWORD" \
  --set=db_name="$POSTGRES_DB" --set=ON_ERROR_STOP=1 <<'SQL'
CREATE ROLE platform_migrator LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD :'migration_password';
CREATE ROLE platform_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD :'app_password';
REVOKE ALL ON DATABASE :"db_name" FROM PUBLIC;
GRANT CONNECT ON DATABASE :"db_name" TO platform_app, platform_migrator;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA public TO platform_migrator;
GRANT CREATE ON DATABASE :"db_name" TO platform_migrator;
ALTER ROLE platform_app SET search_path = platform, public;
ALTER ROLE platform_migrator SET search_path = platform, public;
SQL
