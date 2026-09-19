FROM postgres:18.6-trixie@sha256:4ef4dbc939d61acea57712655ddb4b4ab27419c913f94cca0cd57cb3ea3c2280
COPY --chmod=0555 infrastructure/scripts/init-db.sh /docker-entrypoint-initdb.d/10-roles.sh
