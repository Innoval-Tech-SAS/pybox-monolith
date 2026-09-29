"""Columna variables (JSONB) en flujos_ivr

Revision ID: d1e2f3a4b5c6
Revises: c9d0e1f2a3b4
Create Date: 2026-07-14 01:00:00

Variables por defecto que se envían a Helena para todo el bulk de la campaña
(AMD_*, PJSIP_TRUNK, …) y para las llamadas de prueba del diseñador.

NO se ejecuta automáticamente -- generada para ejecución manual (alembic upgrade head).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, None] = "c9d0e1f2a3b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "flujos_ivr", sa.Column("variables", postgresql.JSONB(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("flujos_ivr", "variables")
