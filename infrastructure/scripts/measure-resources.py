"""Capture point-in-time idle container observations; not a capacity benchmark."""

import json
import re
import subprocess
import time


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True)


def bytes_value(value: str) -> float:
    match = re.fullmatch(r"([0-9.]+)([A-Za-z]+)", value.strip())
    if match is None:
        raise ValueError("Unrecognized Docker memory unit")
    factor = {
        "B": 1,
        "KiB": 1024,
        "MiB": 1024**2,
        "GiB": 1024**3,
        "kB": 1000,
        "MB": 1000**2,
        "GB": 1000**3,
    }[match[2]]
    return float(match[1]) * factor


ids = run("docker", "compose", "ps", "-q").split()
if not ids:
    raise SystemExit("No running Compose containers")
time.sleep(10)  # Let restore/smoke work settle before the idle sample.
rows = [
    json.loads(line)
    for line in run(
        "docker", "stats", "--no-stream", "--format", "{{json .}}", *ids
    ).splitlines()
]
for row in rows:
    print(f"{row['Name']}: memory={row['MemUsage']}, cpu={row['CPUPerc']}")
total = sum(bytes_value(row["MemUsage"].split("/")[0]) for row in rows)
print(f"Total container memory: {total / 1024**2:.2f} MiB (excludes Docker VM/host)")
print(run("docker", "system", "df"))
print(
    "Disk report covers the Docker daemon, including shared layers; not application-only storage."
)

image_ids = sorted(set(run("docker", "compose", "images", "-q").split()))
images = json.loads(run("docker", "image", "inspect", *image_ids))
for image in images:
    print(f"Image {image['Id'][:19]}: {image['Size'] / 1024**2:.2f} MiB (logical size)")
print(
    "Image logical sizes include shared layers; do not sum them as unique disk usage."
)
print(
    "PostgreSQL volume KiB: "
    + run(
        "docker",
        "compose",
        "exec",
        "-T",
        "postgres",
        "du",
        "-sk",
        "/var/lib/postgresql",
    ).strip()
)
