"""empty message

Revision ID: 85593f4880d6
Revises: 3b7d33e79ebb
Create Date: 2023-11-03 09:20:49.744545

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85593f4880d6'
down_revision: Union[str, None] = '3b7d33e79ebb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('media', sa.Column('link_orig', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('media', 'link_orig')
    # ### end Alembic commands ###
