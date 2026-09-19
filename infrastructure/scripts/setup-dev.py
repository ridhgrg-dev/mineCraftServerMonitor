"""Create local development credentials without printing or committing them."""

import argparse
import os
import secrets
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, default=Path(".env"))
path = parser.parse_args().output
if path.exists():
    raise SystemExit(".env already exists; existing configuration was preserved.")
values = {
    key: secrets.token_hex(24)
    for key in ("POSTGRES_PASSWORD", "APP_DB_PASSWORD", "MIGRATION_DB_PASSWORD")
}
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, "w") as stream:
    stream.write("# Local development only. Generated credentials; do not commit.\n")
    stream.writelines(f"{key}={value}\n" for key, value in values.items())
print("Created .env with private development credentials.")
