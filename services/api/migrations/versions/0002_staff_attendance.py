"""Durable employee-wide staff presence, immutable facts/corrections and receipts.

Empty new tables; no backfill. All tenant references are composite and the
runtime cannot update/delete history, audit or receipts. Presence locks serialize
an employee across branches; session uniqueness is an additional DB constraint.
"""

from alembic import op

revision = "0002_staff_attendance"
down_revision = "0001_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE app.staff_presence (
            organization_id uuid NOT NULL, employee_id uuid NOT NULL,
            version integer NOT NULL DEFAULT 0 CHECK(version>=0),
            open_branch_id uuid,open_session_id uuid,
            last_occurred_at timestamptz,last_recorded_at timestamptz,
            PRIMARY KEY(organization_id,employee_id),
            FOREIGN KEY(organization_id,employee_id) REFERENCES app.employees(organization_id,id),
            FOREIGN KEY(organization_id,open_branch_id) REFERENCES app.branches(organization_id,id),
            CHECK((open_branch_id IS NULL)=(open_session_id IS NULL)),
            CHECK((version=0 AND last_occurred_at IS NULL AND last_recorded_at IS NULL AND open_session_id IS NULL)
               OR (version>0 AND last_occurred_at IS NOT NULL AND last_recorded_at IS NOT NULL AND last_recorded_at>=last_occurred_at))
        );
        CREATE UNIQUE INDEX one_staff_open_session ON app.staff_presence(organization_id,open_session_id)
            WHERE open_session_id IS NOT NULL;
        CREATE TABLE app.staff_events (
            organization_id uuid NOT NULL,id uuid NOT NULL,employee_id uuid NOT NULL,
            branch_id uuid NOT NULL,actor_id uuid NOT NULL REFERENCES app.users(id),
            operation_id uuid NOT NULL,session_id uuid NOT NULL,
            action text NOT NULL CHECK(action IN ('check_in','check_out')),
            occurred_at timestamptz NOT NULL,recorded_at timestamptz NOT NULL,
            version integer NOT NULL CHECK(version>0),
            PRIMARY KEY(organization_id,id),UNIQUE(organization_id,employee_id,version),
            UNIQUE(organization_id,session_id,action),UNIQUE(organization_id,id,employee_id),
            FOREIGN KEY(organization_id,employee_id) REFERENCES app.employees(organization_id,id),
            FOREIGN KEY(organization_id,branch_id) REFERENCES app.branches(organization_id,id),
            CHECK(recorded_at>=occurred_at)
        );
        CREATE INDEX staff_events_day ON app.staff_events(organization_id,branch_id,occurred_at,id);
        CREATE TABLE app.staff_corrections (
            organization_id uuid NOT NULL,id uuid NOT NULL,employee_id uuid NOT NULL,event_id uuid NOT NULL,
            actor_id uuid NOT NULL REFERENCES app.users(id),original_at timestamptz NOT NULL,
            corrected_at timestamptz NOT NULL,recorded_at timestamptz NOT NULL,
            reason text NOT NULL CHECK(length(trim(reason)) BETWEEN 3 AND 500),
            version integer NOT NULL CHECK(version>0),
            PRIMARY KEY(organization_id,id),UNIQUE(organization_id,employee_id,version),
            FOREIGN KEY(organization_id,event_id,employee_id) REFERENCES app.staff_events(organization_id,id,employee_id),
            CHECK(corrected_at<=recorded_at)
        );
        CREATE TABLE app.staff_receipts (
            organization_id uuid NOT NULL,actor_id uuid NOT NULL REFERENCES app.users(id),
            operation_id uuid NOT NULL,fingerprint text NOT NULL,response jsonb NOT NULL,
            recorded_at timestamptz NOT NULL,PRIMARY KEY(organization_id,actor_id,operation_id)
        );
    """)
    for table in ("staff_presence", "staff_events", "staff_corrections", "staff_receipts"):
        op.execute(f"ALTER TABLE app.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE app.{table} FORCE ROW LEVEL SECURITY")
        predicate = "organization_id=app.organization_context()"
        if table == "staff_receipts":
            predicate += " AND actor_id=app.actor_context()"
        op.execute(f"CREATE POLICY tenant ON app.{table} USING({predicate})")
        op.execute(f"GRANT SELECT,INSERT ON app.{table} TO nursery_app")
    op.execute("GRANT UPDATE ON app.staff_presence TO nursery_app")


def downgrade() -> None:
    raise RuntimeError("Staff attendance history requires a reviewed forward migration")
