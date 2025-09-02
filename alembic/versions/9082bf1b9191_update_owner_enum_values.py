"""update_owner_enum_values

Revision ID: 9082bf1b9191
Revises: c2c51200b2da
Create Date: 2025-09-02 12:05:01.275725

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9082bf1b9191'
down_revision = 'c2c51200b2da'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # First, convert the enum column to text to remove the constraint
    op.execute("ALTER TABLE influencers ALTER COLUMN owner TYPE text")
    
    # Update existing data to map to new enum values (handle both cases)
    op.execute("UPDATE influencers SET owner = 'samuel' WHERE owner IN ('users', 'cellphone', 'multiple', 'Samuel')")
    
    # Drop the old enum type
    op.execute("DROP TYPE ownertype")
    
    # Create new enum type with proper values  
    op.execute("CREATE TYPE ownertype AS ENUM ('alejandra', 'alessandro', 'bianca', 'jesus', 'julia', 'samuel')")
    
    # Convert the column back to the new enum type
    op.execute("ALTER TABLE influencers ALTER COLUMN owner TYPE ownertype USING owner::ownertype")


def downgrade() -> None:
    # Revert to old enum values
    op.execute("ALTER TABLE influencers ADD COLUMN owner_old ownertype")
    op.execute("UPDATE influencers SET owner_old = 'users'")
    op.execute("ALTER TABLE influencers DROP COLUMN owner")
    op.execute("ALTER TABLE influencers RENAME COLUMN owner_old TO owner")
    
    # Recreate old enum type
    op.execute("DROP TYPE ownertype CASCADE")
    op.execute("CREATE TYPE ownertype AS ENUM ('users', 'cellphone', 'multiple')")
    
    # Update column type
    op.execute("ALTER TABLE influencers ALTER COLUMN owner TYPE ownertype USING 'users'::ownertype")