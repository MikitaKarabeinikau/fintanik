"""add receipt photo to transactions

Revision ID: 45e80b4beac5
Revises: 65757794e587
Create Date: 2026-03-21 11:59:02.086708

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45e80b4beac5'
down_revision: Union[str, Sequence[str], None] = '65757794e587'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('transactions', sa.Column('reciept_photo_name', sa.String(length=255), nullable=True, default=None))

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('transactions', 'reciept_photo_name')