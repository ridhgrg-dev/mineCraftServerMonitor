"""Establish private application schema and future table privileges; no business tables."""

from alembic import op

revision = "0001_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA platform AUTHORIZATION platform_migrator")
    op.execute("GRANT USAGE ON SCHEMA platform TO platform_app")
    op.execute(
        "ALTER DEFAULT PRIVILEGES IN SCHEMA platform "
        "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO platform_app"
    )
    op.execute(
        "ALTER DEFAULT PRIVILEGES IN SCHEMA platform "
        "GRANT USAGE, SELECT ON SEQUENCES TO platform_app"
    )


def downgrade() -> None:
    op.execute("DROP SCHEMA platform")
