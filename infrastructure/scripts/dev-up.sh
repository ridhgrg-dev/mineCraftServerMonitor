#!/bin/sh
set -eu
if [ ! -f .env ]; then python3 infrastructure/scripts/setup-dev.py; fi
docker compose up --build -d --wait postgres redis
docker compose build api worker migrate web
docker compose --profile tools run --rm migrate
docker compose up -d --wait
