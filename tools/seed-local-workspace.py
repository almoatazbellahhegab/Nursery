"""Populate only the owned local synthetic dev/test databases, not production."""

import json
from pathlib import Path

import psycopg

from nursery_api.runtime.bootstrap import seed_workspace

root = Path(__file__).resolve().parents[1]
runtime = json.loads((root / ".tools/database-runtime.json").read_text())
for environment in ("dev", "test"):
    with psycopg.connect(runtime[f"{environment}_owner_url"]) as connection:
        seed_workspace(connection, root / f".tools/{environment}-accounts.json")
print("Fictional workspaces seeded; generated credentials are in ignored local account files.")
