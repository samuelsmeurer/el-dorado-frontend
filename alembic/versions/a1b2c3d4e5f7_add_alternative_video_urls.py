"""add alternative video URLs for fallback

Revision ID: a1b2c3d4e5f7
Revises: 83331dddc462
Create Date: 2025-09-03 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f7'
down_revision = '83331dddc462'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add alternative URL fields to tiktok_videos table
    op.add_column('tiktok_videos', sa.Column('watermark_free_url_alt1', sa.String(length=1000), nullable=True))
    op.add_column('tiktok_videos', sa.Column('watermark_free_url_alt2', sa.String(length=1000), nullable=True))


def downgrade() -> None:
    # Remove alternative URL fields from tiktok_videos table
    op.drop_column('tiktok_videos', 'watermark_free_url_alt2')
    op.drop_column('tiktok_videos', 'watermark_free_url_alt1')