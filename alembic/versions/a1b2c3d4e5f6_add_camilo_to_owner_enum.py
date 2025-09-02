"""add_camilo_to_owner_enum

Revision ID: a1b2c3d4e5f6
Revises: b44341b5a368
Create Date: 2025-09-02 17:22:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'b44341b5a368'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add 'camilo' to the existing enum
    op.execute("ALTER TYPE ownertype ADD VALUE 'camilo'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values directly
    # You would need to recreate the enum without 'camilo' if needed
    pass