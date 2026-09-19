"""Add Phase 2 identity, organization, and membership tables.

The application creates UUIDs. RLS policies use transaction-local identity
settings installed by the authorization layer in the following checkpoint.
"""

from alembic import op

revision = "0002_identity_organizations"
down_revision = "0001_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE platform.users (
            id uuid PRIMARY KEY,
            email_normalized text NOT NULL UNIQUE,
            display_name text NOT NULL,
            password_hash text NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT users_email_normalized_check
                CHECK (email_normalized = lower(email_normalized)),
            CONSTRAINT users_email_nonempty_check
                CHECK (length(email_normalized) BETWEEN 3 AND 320),
            CONSTRAINT users_display_name_nonempty_check
                CHECK (length(display_name) BETWEEN 1 AND 100)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE platform.organizations (
            id uuid PRIMARY KEY,
            name text NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT organizations_name_nonempty_check CHECK (length(name) BETWEEN 1 AND 120)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE platform.organization_memberships (
            id uuid PRIMARY KEY,
            organization_id uuid NOT NULL REFERENCES platform.organizations(id) ON DELETE CASCADE,
            user_id uuid NOT NULL REFERENCES platform.users(id) ON DELETE RESTRICT,
            role text NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT organization_memberships_role_check
                CHECK (role IN ('owner', 'admin', 'member')),
            CONSTRAINT organization_memberships_user_organization_unique
                UNIQUE (user_id, organization_id),
            CONSTRAINT organization_memberships_id_organization_unique
                UNIQUE (id, organization_id)
        )
        """
    )
    op.execute(
        "CREATE INDEX organization_memberships_organization_id_idx "
        "ON platform.organization_memberships (organization_id, user_id)"
    )
    op.execute(
        "CREATE INDEX organization_memberships_user_id_idx "
        "ON platform.organization_memberships (user_id, organization_id)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE platform.organization_memberships")
    op.execute("DROP TABLE platform.organizations")
    op.execute("DROP TABLE platform.users")
