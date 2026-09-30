"""Etiquetas de resultado IVR: flujos_ivr.resultados + tipificacion por interaccion

Revision ID: f3a4b5c6d7e8
Revises: e2f3a4b5c6d7
Create Date: 2026-09-14 02:00:00

Fase 6 del plan `ivr-helena`: el desenlace tecnico de una llamada
(`ivrEndNodeId` + `ivrEndReason`) se traduce a una etiqueta de negocio libre,
configurada por nodo en el disenador y resuelta al cerrar cada llamada.

NO se ejecuta automaticamente -- generada para ejecucion manual por el usuario
(alembic upgrade head).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "f3a4b5c6d7e8"
down_revision: Union[str, None] = "e2f3a4b5c6d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Mapa {nombre_nodo: {clave: etiqueta}} compilado desde el disenador.
    op.add_column(
        "flujos_ivr", sa.Column("resultados", postgresql.JSONB(), nullable=True)
    )

    op.add_column(
        "interacciones_ivr",
        sa.Column("clave_resultado", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "interacciones_ivr",
        sa.Column("etiqueta_resultado", sa.String(length=255), nullable=True),
    )
    op.create_index(
        "ix_interacciones_ivr_clave_resultado",
        "interacciones_ivr",
        ["clave_resultado"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_interacciones_ivr_clave_resultado", table_name="interacciones_ivr"
    )
    op.drop_column("interacciones_ivr", "etiqueta_resultado")
    op.drop_column("interacciones_ivr", "clave_resultado")
    op.drop_column("flujos_ivr", "resultados")
