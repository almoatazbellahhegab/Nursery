"""Initialize an owned loopback-only PostgreSQL runtime; generate local secrets.

Only .tools/postgres-data is managed. No Windows service, machine policy or global
database is modified. Runtime files/accounts are ignored and never printed.
"""

import json
import os
import secrets
import subprocess
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import quote

import psycopg
from psycopg import sql

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / ".tools"
BIN = TOOLS / "postgres" / "pgsql" / "bin"
DATA = TOOLS / "postgres-data"
RUNTIME = TOOLS / "database-runtime.json"
FLAGS = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


def run(args: list[str], *, env: dict[str, str] | None = None) -> None:
    subprocess.run(args, check=True, env=env, creationflags=FLAGS)


def main() -> None:
    if not BIN.exists():
        destination = (TOOLS / "postgres").resolve()
        with zipfile.ZipFile(TOOLS / "postgresql-18.6-windows.zip") as archive:
            for item in archive.infolist():
                if not item.filename.startswith(("pgsql/bin/", "pgsql/lib/", "pgsql/share/")):
                    continue
                target = (destination / item.filename).resolve()
                if not target.is_relative_to(destination):
                    raise RuntimeError("Unsafe archive path")
                archive.extract(item, destination)
    if RUNTIME.exists():
        config = json.loads(RUNTIME.read_text())
    else:
        config = {"owner_password": secrets.token_urlsafe(32), "app_password": secrets.token_urlsafe(32)}
        RUNTIME.write_text(json.dumps(config, indent=2))
    if not (DATA / "PG_VERSION").exists():
        with tempfile.NamedTemporaryFile(mode="w", dir=TOOLS, delete=False) as password:
            password.write(config["owner_password"])
            password_path = Path(password.name)
        try:
            run([str(BIN / "initdb.exe"), "-D", str(DATA), "-U", "nursery_owner",
                 "--auth=scram-sha-256", "--encoding=UTF8", "--locale=C",
                 f"--pwfile={password_path}"])
        finally:
            password_path.unlink()
    status = subprocess.run([str(BIN / "pg_ctl.exe"), "-D", str(DATA), "status"],
                            capture_output=True, creationflags=FLAGS)
    if status.returncode != 0:
        run([str(BIN / "pg_ctl.exe"), "-D", str(DATA), "-l", str(TOOLS / "postgres.log"),
             "-o", "-p 55432 -h 127.0.0.1", "-w", "start"])
    owner = f"postgresql://nursery_owner:{quote(config['owner_password'])}@127.0.0.1:55432/"
    with psycopg.connect(owner + "postgres", autocommit=True) as connection:
        if not connection.execute("SELECT 1 FROM pg_roles WHERE rolname='nursery_app'").fetchone():
            connection.execute(sql.SQL(
                "CREATE ROLE nursery_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS PASSWORD {}"
            ).format(sql.Literal(config["app_password"])))
        for name in ("nursery_dev", "nursery_test"):
            if not connection.execute("SELECT 1 FROM pg_database WHERE datname=%s", (name,)).fetchone():
                connection.execute(sql.SQL("CREATE DATABASE {} OWNER nursery_owner").format(sql.Identifier(name)))
    config["dev_owner_url"] = owner + "nursery_dev"
    config["test_owner_url"] = owner + "nursery_test"
    app_url = f"postgresql://nursery_app:{quote(config['app_password'])}@127.0.0.1:55432/"
    config["dev_url"], config["test_url"] = app_url + "nursery_dev", app_url + "nursery_test"
    RUNTIME.write_text(json.dumps(config, indent=2))
    for name in ("dev", "test"):
        environment = dict(os.environ, NURSERY_MIGRATION_URL=config[f"{name}_owner_url"])
        run([str(ROOT / "services/api/.venv/Scripts/python.exe"), "-m", "alembic",
             "-c", str(ROOT / "services/api/alembic.ini"), "upgrade", "head"], env=environment)
    print("Owned PostgreSQL ready on loopback port 55432; dev/test migrations applied.")


if __name__ == "__main__":
    main()
