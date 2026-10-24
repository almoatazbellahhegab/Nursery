"""Rotate the owned local runtime role; never print DSNs or generated passwords."""

import json
import secrets
from pathlib import Path
from urllib.parse import quote, urlsplit

import psycopg
from psycopg import sql

runtime = Path(__file__).resolve().parents[1] / ".tools/database-runtime.json"
config = json.loads(runtime.read_text())
if urlsplit(config["dev_owner_url"]).hostname != "127.0.0.1":
    raise RuntimeError("Only the project-owned loopback runtime may be rotated")
password = secrets.token_urlsafe(32)
with psycopg.connect(config["dev_owner_url"]) as connection:
    connection.execute(sql.SQL("ALTER ROLE nursery_app PASSWORD {}").format(sql.Literal(password)))
config["app_password"] = password
for environment in ("dev", "test"):
    config[f"{environment}_url"] = f"postgresql://nursery_app:{quote(password)}@127.0.0.1:55432/nursery_{environment}"
runtime.write_text(json.dumps(config, indent=2))
print("Project-local application database credential rotated.")
