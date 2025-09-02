"""force_clean_owner_enum

Revision ID: b44341b5a368
Revises: 9082bf1b9191
Create Date: 2025-09-02 12:12:16.124407

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b44341b5a368'
down_revision = '9082bf1b9191'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Force cleanup - handle any state the database might be in
    try:
        # Convert to text first (might already be text from previous migration attempt)
        op.execute("ALTER TABLE influencers ALTER COLUMN owner TYPE text")
    except:
        pass
    
    # Clean up all possible owner values to 'samuel'
    op.execute("""
        UPDATE influencers 
        SET owner = 'samuel' 
        WHERE owner IN ('users', 'cellphone', 'multiple', 'Samuel', 'SAMUEL', 'alejandra', 'alessandro', 'bianca', 'jesus', 'julia')
           OR owner IS NULL
    """)
    
    # Drop enum if exists
    try:
        op.execute("DROP TYPE IF EXISTS ownertype CASCADE")
    except:
        pass
    
    # Create clean enum
    op.execute("CREATE TYPE ownertype AS ENUM ('alejandra', 'alessandro', 'bianca', 'jesus', 'julia', 'samuel')")
    
    # Convert column to enum
    op.execute("ALTER TABLE influencers ALTER COLUMN owner TYPE ownertype USING 'samuel'::ownertype")


def downgrade() -> None:
    pass