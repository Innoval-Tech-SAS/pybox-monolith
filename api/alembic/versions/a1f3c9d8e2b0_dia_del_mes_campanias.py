"""dia del mes para campañas mensuales

Revision ID: a1f3c9d8e2b0
Revises: 4e6920dd7492
Create Date: 2026-06-19 06:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1f3c9d8e2b0'
down_revision: Union[str, None] = '4e6920dd7492'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('campanias', sa.Column('dia_del_mes', sa.Integer(), nullable=True))
    op.add_column('programacion_campanias', sa.Column('dia_del_mes', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('programacion_campanias', 'dia_del_mes')
    op.drop_column('campanias', 'dia_del_mes')
