"""Expand session lineage/absolute expiry and provider-attempt surface; no backfill.

Nullable fields preserve existing sessions without rewriting their rows. Readers
derive legacy expiry/lineage until a session rotates. Expected identity tables
are below 10k rows here; metadata/FK validation locks last seconds. Verify nullable
legacy reads and that replacement targets stay inside the application-owned
session family. Recover forward; do not delete session or security history.
"""

from alembic import op

revision = "0005_session_rotation"
down_revision = "0004_identity_security"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE app.sessions ADD COLUMN family_id uuid,
            ADD COLUMN absolute_expires_at timestamptz,
            ADD COLUMN replaced_by_hash text REFERENCES app.sessions(token_hash),
            ADD CONSTRAINT valid_session_replacement CHECK(
                replaced_by_hash IS NULL OR (family_id IS NOT NULL AND replaced_by_hash<>token_hash)
            ),
            ADD CONSTRAINT valid_absolute_expiry CHECK(
                absolute_expires_at IS NULL OR absolute_expires_at>authenticated_at
            );
        CREATE INDEX session_family_lookup ON app.sessions(user_id,organization_id,family_id);
        ALTER TABLE app.oidc_attempts ADD COLUMN surface text NOT NULL DEFAULT 'web'
            CHECK(surface IN ('web','mobile_web','native'));
    """)


def downgrade() -> None:
    raise RuntimeError("Preserve session lineage; use a forward migration")
