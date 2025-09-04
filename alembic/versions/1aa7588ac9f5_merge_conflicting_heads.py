"""merge conflicting heads

Revision ID: 1aa7588ac9f5
Revises: a1b2c3d4e5f7, dbf407b8a5a5
Create Date: 2025-09-03 21:54:04.234535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1aa7588ac9f5'
down_revision = ('a1b2c3d4e5f7', 'dbf407b8a5a5')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass