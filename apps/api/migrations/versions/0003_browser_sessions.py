"""Add revocable opaque browser sessions."""

from alembic import op

revision = "0003_browser_sessions"
down_revision = "0002_identity_organizations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE platform.browser_sessions (
            id uuid PRIMARY KEY,
            user_id uuid NOT NULL REFERENCES platform.users(id) ON DELETE CASCADE,
            token_hash bytea NOT NULL UNIQUE,
            expires_at timestamptz NOT NULL,
            revoked_at timestamptz,
            created_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT browser_sessions_expiry_check CHECK (expires_at > created_at)
        )
        """
    )
    op.execute(
        "CREATE INDEX browser_sessions_active_user_idx "
        "ON platform.browser_sessions (user_id, expires_at) WHERE revoked_at IS NULL"
    )


def downgrade() -> None:
    op.execute("DROP TABLE platform.browser_sessions")
