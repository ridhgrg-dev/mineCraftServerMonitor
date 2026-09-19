"""Export contracts without opening sockets or requiring live dependencies."""

import json
from pathlib import Path

from control_plane.core.settings import Settings
from control_plane.main import create_app
from pydantic import SecretStr

root = Path(__file__).resolve().parents[2]
app = create_app(
    Settings(
        environment="test",
        database_url=SecretStr("postgresql+psycopg://schema@localhost/schema"),
    )
)
(root / "packages/api-client/openapi.json").write_text(
    json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"
)
