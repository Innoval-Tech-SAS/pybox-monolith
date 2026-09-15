"""Politica de contacto por flujo IVR (flujos_ivr.id_politica_contacto)

Revision ID: b5c6d7e8f9a0
Revises: a4b5c6d7e8f9
Create Date: 2026-09-14 04:00:00

Fase 8 del plan `ivr-helena`: el flujo puede apuntar a una politica de contacto
de Helena (horario permitido de marcacion, festivos y excepciones). Solo se
guarda el id -- las ventanas las administra Helena.

Los nodos `condition` y `hangup` de esta misma fase NO requieren migracion: son
estructura dentro del JSONB `config`/`grafo` que ya existe.

NO se ejecuta automaticamente -- generada para ejecucion manual por el usuario
(alembic upgrade head).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b5c6d7e8f9a0"
down_revision: Union[str, None] = "a4b5c6d7e8f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "flujos_ivr", sa.Column("id_politica_contacto", sa.String(length=64), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("flujos_ivr", "id_politica_contacto")
