"""Validate resolved production config read from stdin; never print secrets."""

import json
import sys

config = json.load(sys.stdin)
for name, service in config["services"].items():
    ports = service.get("ports", [])
    if name != "caddy" and ports:
        raise SystemExit(f"Unexpected public ports on {name}")
    if name == "caddy":
        assert {int(p["published"]) for p in ports} == {80, 443}
    assert not any(v["type"] == "bind" for v in service.get("volumes", [])), name
    assert service.get("restart") in {"unless-stopped", "no"}, name
    assert "latest" not in service.get("image", ""), name
assert config["networks"]["data"]["internal"]
assert config["networks"]["application"]["internal"]
print(
    "PASS: only Caddy publishes 80/443; private networks; no bind mounts or floating latest tags."
)
