"""Expand branch metadata and shared command receipts; no data rewrite.

Existing branches retain Cairo timezone and active status. Brief metadata locks
on the small branch/membership tables; additive defaults require no backfill.
Validate version>0 and FORCE RLS after upgrade. Recover with a forward migration.
"""

from alembic import op

revision = "0003_branch_management"
down_revision = "0002_staff_attendance"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE app.branches
            ADD COLUMN timezone text NOT NULL DEFAULT 'Africa/Cairo',
            ADD COLUMN contact_email text NOT NULL DEFAULT '' CHECK(length(contact_email)<=254),
            ADD COLUMN contact_phone text NOT NULL DEFAULT '' CHECK(length(contact_phone)<=40),
            ADD COLUMN address text NOT NULL DEFAULT '' CHECK(length(address)<=500),
            ADD COLUMN capacity integer CHECK(capacity BETWEEN 1 AND 10000),
            ADD COLUMN operating_status text NOT NULL DEFAULT 'open'
                CHECK(operating_status IN ('planned','open','temporarily_closed')),
            ADD COLUMN version integer NOT NULL DEFAULT 1 CHECK(version>0);
        CREATE POLICY admin_memberships ON app.memberships FOR SELECT USING(
            organization_id=app.organization_context() AND current_setting('app.role',true)='administrator'
        );
        DROP POLICY self_branches ON app.branch_memberships;
        CREATE POLICY branch_membership_scope ON app.branch_memberships FOR SELECT USING(
            organization_id=app.organization_context() AND
            (user_id=app.actor_context() OR current_setting('app.role',true)='administrator')
        );
        CREATE POLICY branch_membership_insert ON app.branch_memberships FOR INSERT WITH CHECK(
            organization_id=app.organization_context() AND current_setting('app.role',true)='administrator'
        );
        CREATE POLICY branch_membership_delete ON app.branch_memberships FOR DELETE USING(
            organization_id=app.organization_context() AND current_setting('app.role',true)='administrator'
        );
        DROP POLICY tenant_branch ON app.branches;
        CREATE POLICY branch_read ON app.branches FOR SELECT USING(
            organization_id=app.organization_context() AND app.branch_allowed(id)
        );
        CREATE POLICY branch_insert ON app.branches FOR INSERT WITH CHECK(
            organization_id=app.organization_context() AND current_setting('app.role',true)='administrator'
        );
        CREATE POLICY branch_update ON app.branches FOR UPDATE USING(
            organization_id=app.organization_context() AND current_setting('app.role',true)='administrator'
        ) WITH CHECK(
            organization_id=app.organization_context() AND current_setting('app.role',true)='administrator'
        );
        GRANT INSERT,UPDATE ON app.branches TO nursery_app;
        GRANT INSERT,DELETE ON app.branch_memberships TO nursery_app;
        CREATE TABLE app.command_receipts (
            organization_id uuid NOT NULL REFERENCES app.organizations(id),
            actor_id uuid NOT NULL REFERENCES app.users(id),operation_id uuid NOT NULL,
            fingerprint text NOT NULL,response jsonb NOT NULL,recorded_at timestamptz NOT NULL,
            PRIMARY KEY(organization_id,actor_id,operation_id)
        );
        ALTER TABLE app.command_receipts ENABLE ROW LEVEL SECURITY;
        ALTER TABLE app.command_receipts FORCE ROW LEVEL SECURITY;
        CREATE POLICY actor_receipt ON app.command_receipts USING(
            organization_id=app.organization_context() AND actor_id=app.actor_context()
        );
        GRANT SELECT,INSERT ON app.command_receipts TO nursery_app;
    """)


def downgrade() -> None:
    raise RuntimeError("Preserve branch and receipt history; use a forward migration")
