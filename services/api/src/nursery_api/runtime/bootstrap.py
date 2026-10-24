"""Explicit fictional local workspace bootstrap, never runs during API startup.

Owner DSN/account-file paths are provided by the local setup wrapper. Passwords
are cryptographically generated and written only to an ignored local file.
This is not public registration and must not be run against real tenant data.
"""

import json
import secrets
from datetime import UTC, datetime
from pathlib import Path
from uuid import NAMESPACE_URL, UUID, uuid5

from psycopg import Connection

from .security import password_hash


def identifier(value: str) -> UUID:
    return uuid5(NAMESPACE_URL, "nursery-fictional-runtime:" + value)


def seed_workspace(connection: Connection[object], account_file: Path) -> dict[str, object]:
    """Idempotent synthetic workspace seed; credentials remain local-only."""
    accounts = json.loads(account_file.read_text()) if account_file.exists() else {}
    created: dict[str, object] = {}
    for tenant in ("garden", "neighbor"):
        org = identifier(tenant)
        connection.execute(
            "INSERT INTO app.organizations(id,name) VALUES(%s,%s) ON CONFLICT DO NOTHING",
            (
                org,
                "Little Garden — fictional"
                if tenant == "garden"
                else "Neighbor Nursery — fictional",
            ),
        )
        for branch in ("maadi", "cairo"):
            connection.execute(
                "INSERT INTO app.branches(organization_id,id,name) VALUES(%s,%s,%s) ON CONFLICT DO NOTHING",
                (org, identifier(tenant + branch), "Maadi" if branch == "maadi" else "New Cairo"),
            )
        for role in ("administrator", "branch_manager", "teacher", "parent", "finance"):
            email = f"{role}@{tenant}.example.test"
            user = identifier(email)
            password = accounts.get(email, secrets.token_urlsafe(24))
            accounts[email] = password
            connection.execute(
                "INSERT INTO app.users(id,email,password_hash) VALUES(%s,%s,%s) ON CONFLICT DO NOTHING",
                (user, email, password_hash(password)),
            )
            connection.execute(
                "INSERT INTO app.memberships(organization_id,user_id,role) VALUES(%s,%s,%s) ON CONFLICT DO NOTHING",
                (org, user, role),
            )
            branches = ("maadi",) if role == "branch_manager" else ("maadi", "cairo")
            for branch in branches:
                connection.execute(
                    "INSERT INTO app.branch_memberships VALUES(%s,%s,%s) ON CONFLICT DO NOTHING",
                    (org, user, identifier(tenant + branch)),
                )
            if role not in {"parent", "finance"}:
                employee = identifier(email + ":employee")
                connection.execute(
                    "INSERT INTO app.employees(organization_id,id,user_id,display_name) "
                    "VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                    (org, employee, user, f"{role.replace('_', ' ').title()} Demo"),
                )
                for branch in branches:
                    connection.execute(
                        "INSERT INTO app.employee_assignments VALUES(%s,%s,%s,%s,NULL) ON CONFLICT DO NOTHING",
                        (
                            org,
                            employee,
                            identifier(tenant + branch),
                            datetime(2026, 1, 1, tzinfo=UTC),
                        ),
                    )
            created[email] = {"user_id": str(user), "organization_id": str(org)}
    account_file.write_text(json.dumps(accounts, indent=2))
    return created
