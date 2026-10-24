"""Add encrypted one-flow authentication receipts; no rewrite or external calls.

Nullable metadata-only expansion on bounded pre-authentication attempts. Completed
responses contain encrypted session material and expire with their login attempt.
Validate all result columns are populated together; preserve attempts on recovery.
"""

from alembic import op

revision = "0006_oidc_results"
down_revision = "0005_session_rotation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE app.oidc_attempts ADD COLUMN result_cipher text,
            ADD COLUMN result_fingerprint text,
            ADD COLUMN completed_at timestamptz,
            ADD CONSTRAINT complete_oidc_result CHECK(
                (result_cipher IS NULL)=(result_fingerprint IS NULL) AND
                (result_cipher IS NULL)=(completed_at IS NULL) AND
                (result_cipher IS NULL OR consumed)
            );
        ALTER TABLE app.sessions ADD CONSTRAINT valid_factor_time CHECK(
            mfa_at IS NULL OR (mfa_at>=authenticated_at AND
            mfa_at<coalesce(absolute_expires_at,authenticated_at+interval '12 hours'))
        );
        CREATE INDEX oidc_attempt_expiry ON app.oidc_attempts(expires_at);
        CREATE INDEX oidc_token_use_expiry ON app.oidc_token_uses(expires_at);
    """)


def downgrade() -> None:
    raise RuntimeError("Preserve authentication receipts; use a forward migration")
