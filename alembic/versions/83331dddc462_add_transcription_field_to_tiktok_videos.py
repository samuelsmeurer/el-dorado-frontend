"""add transcription field to tiktok_videos

Revision ID: 83331dddc462
Revises: a1b2c3d4e5f6
Create Date: 2025-09-03 09:56:47.688554

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83331dddc462'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add transcription field to tiktok_videos table
    op.add_column('tiktok_videos', sa.Column('transcription', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove transcription field from tiktok_videos table
    op.drop_column('tiktok_videos', 'transcription')