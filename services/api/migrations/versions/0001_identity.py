"""Tenant/identity foundation; empty-schema upgrade, no production data backfill.

Creates constrained UUID tenant references, hashed-password/session storage and
FORCE RLS. Owner credentials are used only for migration/bootstrap; the API role
is NOSUPERUSER/NOBYPASSRLS. Rollback requires explicit review because it removes
identity data. Expected empty-schema lock time is seconds, not an online rewrite.
"""

from alembic import op

revision = "0001_identity"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE SCHEMA app;
        CREATE TABLE app.organizations (
            id uuid PRIMARY KEY, name text NOT NULL CHECK(length(name) BETWEEN 1 AND 160),
            active boolean NOT NULL DEFAULT true,
            timezone text NOT NULL DEFAULT 'Africa/Cairo'
        );
        CREATE TABLE app.users (
            id uuid PRIMARY KEY, email text NOT NULL UNIQUE,
            password_hash text NOT NULL, active boolean NOT NULL DEFAULT true,
            CHECK(email = lower(email))
        );
        CREATE TABLE app.branches (
            organization_id uuid NOT NULL REFERENCES app.organizations(id),
            id uuid NOT NULL, name text NOT NULL CHECK(length(name) BETWEEN 1 AND 160),
            active boolean NOT NULL DEFAULT true,
            PRIMARY KEY(organization_id,id)
        );
        CREATE TABLE app.memberships (
            organization_id uuid NOT NULL REFERENCES app.organizations(id),
            user_id uuid NOT NULL REFERENCES app.users(id),
            role text NOT NULL CHECK(role IN (
                'administrator','branch_manager','teacher','parent','finance','driver'
            )), active boolean NOT NULL DEFAULT true,
            PRIMARY KEY(organization_id,user_id)
        );
        CREATE TABLE app.branch_memberships (
            organization_id uuid NOT NULL, user_id uuid NOT NULL, branch_id uuid NOT NULL,
            PRIMARY KEY(organization_id,user_id,branch_id),
            FOREIGN KEY(organization_id,user_id) REFERENCES app.memberships(organization_id,user_id),
            FOREIGN KEY(organization_id,branch_id) REFERENCES app.branches(organization_id,id)
        );
        CREATE TABLE app.employees (
            organization_id uuid NOT NULL REFERENCES app.organizations(id),
            id uuid NOT NULL, user_id uuid REFERENCES app.users(id),
            display_name text NOT NULL CHECK(length(display_name) BETWEEN 1 AND 160),
            active boolean NOT NULL DEFAULT true, version integer NOT NULL DEFAULT 1 CHECK(version>0),
            PRIMARY KEY(organization_id,id), UNIQUE(organization_id,user_id),
            FOREIGN KEY(organization_id,user_id) REFERENCES app.memberships(organization_id,user_id)
        );
        CREATE TABLE app.employee_assignments (
            organization_id uuid NOT NULL, employee_id uuid NOT NULL, branch_id uuid NOT NULL,
            starts_at timestamptz NOT NULL, ends_at timestamptz,
            PRIMARY KEY(organization_id,employee_id,branch_id,starts_at),
            FOREIGN KEY(organization_id,employee_id) REFERENCES app.employees(organization_id,id),
            FOREIGN KEY(organization_id,branch_id) REFERENCES app.branches(organization_id,id),
            CHECK(ends_at IS NULL OR ends_at > starts_at)
        );
        CREATE INDEX employee_assignment_lookup ON app.employee_assignments
            (organization_id,branch_id,employee_id);
        CREATE TABLE app.sessions (
            token_hash text PRIMARY KEY, user_id uuid NOT NULL REFERENCES app.users(id),
            organization_id uuid NOT NULL REFERENCES app.organizations(id),
            expires_at timestamptz NOT NULL, last_seen_at timestamptz NOT NULL,
            revoked boolean NOT NULL DEFAULT false,
            FOREIGN KEY(organization_id,user_id) REFERENCES app.memberships(organization_id,user_id)
        );
        CREATE TABLE app.login_limits (
            key_hash text PRIMARY KEY, started_at timestamptz NOT NULL,
            failures integer NOT NULL DEFAULT 0 CHECK(failures>=0)
        );
        CREATE TABLE app.audit (
            organization_id uuid NOT NULL REFERENCES app.organizations(id),
            id uuid NOT NULL, actor_id uuid NOT NULL REFERENCES app.users(id),
            action text NOT NULL, resource_id uuid NOT NULL,
            recorded_at timestamptz NOT NULL, details jsonb NOT NULL DEFAULT '{}',
            PRIMARY KEY(organization_id,id)
        );
        CREATE INDEX audit_resource_time ON app.audit(organization_id,resource_id,recorded_at,id);
        CREATE FUNCTION app.organization_context() RETURNS uuid LANGUAGE sql STABLE AS
            $$ SELECT nullif(current_setting('app.organization_id',true),'')::uuid $$;
        CREATE FUNCTION app.actor_context() RETURNS uuid LANGUAGE sql STABLE AS
            $$ SELECT nullif(current_setting('app.actor_id',true),'')::uuid $$;
        CREATE FUNCTION app.branch_allowed(branch uuid) RETURNS boolean LANGUAGE sql STABLE AS
            $$ SELECT current_setting('app.role',true)='administrator' OR EXISTS(
                SELECT 1 FROM app.branch_memberships bm WHERE
                bm.organization_id=app.organization_context() AND bm.user_id=app.actor_context()
                AND bm.branch_id=branch
            ) $$;
        ALTER TABLE app.organizations ENABLE ROW LEVEL SECURITY;
        ALTER TABLE app.organizations FORCE ROW LEVEL SECURITY;
        CREATE POLICY tenant ON app.organizations USING(id=app.organization_context());
        ALTER TABLE app.memberships ENABLE ROW LEVEL SECURITY;
        ALTER TABLE app.memberships FORCE ROW LEVEL SECURITY;
        CREATE POLICY self_membership ON app.memberships USING(user_id=app.actor_context());
        ALTER TABLE app.branch_memberships ENABLE ROW LEVEL SECURITY;
        ALTER TABLE app.branch_memberships FORCE ROW LEVEL SECURITY;
        CREATE POLICY self_branches ON app.branch_memberships USING(
            organization_id=app.organization_context() AND user_id=app.actor_context()
        );
        ALTER TABLE app.branches ENABLE ROW LEVEL SECURITY;
        ALTER TABLE app.branches FORCE ROW LEVEL SECURITY;
        CREATE POLICY tenant_branch ON app.branches USING(
            organization_id=app.organization_context() AND app.branch_allowed(id)
        );
    """)
    for table in ("employees", "employee_assignments", "audit"):
        op.execute(f"ALTER TABLE app.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE app.{table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY tenant ON app.{table} USING(organization_id=app.organization_context())"
        )
    op.execute("""
        GRANT USAGE ON SCHEMA app TO nursery_app;
        GRANT SELECT ON app.organizations,app.branches,app.memberships,app.branch_memberships,
            app.employees,app.employee_assignments TO nursery_app;
        GRANT SELECT,INSERT,UPDATE,DELETE ON app.sessions,app.login_limits TO nursery_app;
        GRANT SELECT ON app.users TO nursery_app;
        GRANT SELECT,INSERT ON app.audit TO nursery_app;
        GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA app TO nursery_app;
    """)


def downgrade() -> None:
    raise RuntimeError("Identity rollback removes access records; use a reviewed forward migration")
