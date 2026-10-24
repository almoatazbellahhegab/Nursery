"""Add provider identities, bounded login attempts and encrypted MFA enrollment.

Additive migration on small identity tables. Existing sessions retain their
expiry and start with no second-factor proof. New columns use metadata defaults;
no tenant data rewrite. Validate FORCE RLS/self policies and nullable MFA proof.
Recovery is a forward migration; never drop identity or recovery history.
"""

from alembic import op

revision = "0004_identity_security"
down_revision = "0003_branch_management"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE app.sessions ADD COLUMN authenticated_at timestamptz NOT NULL DEFAULT now(),
            ADD COLUMN mfa_at timestamptz;
        CREATE TABLE app.external_identities (
            issuer text NOT NULL,subject text NOT NULL,user_id uuid NOT NULL REFERENCES app.users(id),
            active boolean NOT NULL DEFAULT true,
            PRIMARY KEY(issuer,subject),UNIQUE(issuer,user_id),
            CHECK(length(issuer) BETWEEN 1 AND 500),CHECK(length(subject) BETWEEN 1 AND 255)
        );
        CREATE TABLE app.oidc_attempts (
            state_hash text PRIMARY KEY,binding_hash text NOT NULL,provider text NOT NULL,
            verifier text NOT NULL,nonce text NOT NULL,organization_id uuid,
            expires_at timestamptz NOT NULL,consumed boolean NOT NULL DEFAULT false
        );
        CREATE TABLE app.oidc_token_uses (
            token_hash text PRIMARY KEY,expires_at timestamptz NOT NULL
        );
        CREATE TABLE app.mfa_enrollments (
            user_id uuid PRIMARY KEY REFERENCES app.users(id),
            secret_cipher text,activated_at timestamptz,last_counter bigint NOT NULL DEFAULT -1,
            pending_cipher text,pending_session_hash text,pending_at timestamptz,
            failures integer NOT NULL DEFAULT 0 CHECK(failures>=0),
            window_started_at timestamptz NOT NULL DEFAULT now(),
            CHECK((secret_cipher IS NULL)=(activated_at IS NULL)),
            CHECK((pending_cipher IS NULL)=(pending_session_hash IS NULL)),
            CHECK((pending_cipher IS NULL)=(pending_at IS NULL))
        );
        CREATE TABLE app.mfa_recovery_codes (
            user_id uuid NOT NULL REFERENCES app.users(id),code_hash text NOT NULL,
            created_at timestamptz NOT NULL,used_at timestamptz,
            PRIMARY KEY(user_id,code_hash)
        );
        ALTER TABLE app.mfa_enrollments ENABLE ROW LEVEL SECURITY;
        ALTER TABLE app.mfa_enrollments FORCE ROW LEVEL SECURITY;
        CREATE POLICY own_mfa ON app.mfa_enrollments USING(user_id=app.actor_context());
        ALTER TABLE app.mfa_recovery_codes ENABLE ROW LEVEL SECURITY;
        ALTER TABLE app.mfa_recovery_codes FORCE ROW LEVEL SECURITY;
        CREATE POLICY own_recovery ON app.mfa_recovery_codes USING(user_id=app.actor_context());
        CREATE TABLE app.auth_receipts (
            user_id uuid NOT NULL REFERENCES app.users(id),session_hash text NOT NULL,
            operation_id uuid NOT NULL,fingerprint text NOT NULL,response_cipher text NOT NULL,
            created_at timestamptz NOT NULL,PRIMARY KEY(user_id,session_hash,operation_id)
        );
        ALTER TABLE app.auth_receipts ENABLE ROW LEVEL SECURITY;
        ALTER TABLE app.auth_receipts FORCE ROW LEVEL SECURITY;
        CREATE POLICY own_auth_receipt ON app.auth_receipts USING(user_id=app.actor_context());
        GRANT SELECT ON app.external_identities TO nursery_app;
        GRANT SELECT,INSERT,UPDATE ON app.oidc_attempts TO nursery_app;
        GRANT SELECT,INSERT ON app.oidc_token_uses TO nursery_app;
        GRANT SELECT,INSERT,UPDATE ON app.mfa_enrollments,app.mfa_recovery_codes TO nursery_app;
        GRANT SELECT,INSERT ON app.auth_receipts TO nursery_app;
    """)


def downgrade() -> None:
    raise RuntimeError("Identity security history must be retained; use a forward migration")
