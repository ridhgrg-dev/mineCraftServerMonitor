"""Run real integration tests using generated local Compose credentials."""

import os
import subprocess
from pathlib import Path
from urllib.parse import quote

values = dict(
    line.split("=", 1)
    for line in Path(os.environ.get("COMPOSE_ENV_FILES", ".env"))
    .read_text()
    .splitlines()
    if line and not line.startswith("#")
)
environment = dict(os.environ)
environment["TEST_DATABASE_URL"] = (
    "postgresql+psycopg://platform_app:"
    + quote(values["APP_DB_PASSWORD"], safe="")
    + "@127.0.0.1:5432/platform"
)
environment["TEST_REDIS_URL"] = "redis://127.0.0.1:6379/15"
subprocess.run(
    [
        "uv",
        "run",
        "--project",
        "apps/api",
        "--frozen",
        "pytest",
        "apps/api/tests",
        "-m",
        "integration",
        "-q",
    ],
    env=environment,
    check=True,
)
