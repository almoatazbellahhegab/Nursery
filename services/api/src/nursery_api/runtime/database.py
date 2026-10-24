"""Short PostgreSQL transactions, with transaction-local tenant/actor/role context."""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row

Row = dict[str, Any]
Connection = psycopg.Connection[Row]


@dataclass(frozen=True)
class Database:
    """API DSN must use the restricted application role, never the migration owner."""

    url: str

    @contextmanager
    def transaction(self) -> Iterator[Connection]:
        with psycopg.connect(self.url, row_factory=dict_row, connect_timeout=5) as connection:
            yield connection


def set_context(connection: Connection, actor: UUID, organization: UUID, role: str = "") -> None:
    """Only server-validated context is accepted; SET LOCAL cannot leak between requests."""
    connection.execute(
        "SELECT set_config('app.actor_id',%s,true),set_config('app.organization_id',%s,true),"
        "set_config('app.role',%s,true)",
        (str(actor), str(organization), role),
    )
