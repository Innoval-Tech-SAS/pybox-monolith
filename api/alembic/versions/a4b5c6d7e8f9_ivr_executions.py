"""Tabla ejecuciones_ivr + ritmo de marcacion en flujos_ivr

Revision ID: a4b5c6d7e8f9
Revises: f3a4b5c6d7e8
Create Date: 2026-09-14 03:00:00

Fase 7 del plan `ivr-helena`: control de campanas IVR en vuelo (pausar,
reanudar, cancelar, ajustar ritmo). Crea la tabla que traza cada bulk
despachado a Helena y agrega a `flujos_ivr` el ritmo/caller ID por defecto con
el que se despachan sus bulks.

NO se ejecuta automaticamente -- generada para ejecucion manual por el usuario
(alembic upgrade head).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a4b5c6d7e8f9"
down_revision: Union[str, None] = "f3a4b5c6d7e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_EXECUTION_STATUS_ENUM_NAME = "ivrexecutionstatus"
_EXECUTION_STATUS_VALUES = ("PENDING", "RUNNING", "PAUSED", "CANCELLED", "FINISHED")


def upgrade() -> None:
    # `create_type=False` es imprescindible: sin él, `op.create_table` vuelve a
    # emitir su propio CREATE TYPE al encontrar la columna que usa este enum y
    # la migración falla con "type ... already exists" (ver e2f3a4b5c6d7, donde
    # se detectó este problema por primera vez). El tipo se crea explícitamente
    # antes, con checkfirst para que la migración sea reejecutable.
    execution_status = postgresql.ENUM(
        *_EXECUTION_STATUS_VALUES, name=_EXECUTION_STATUS_ENUM_NAME, create_type=False
    )
    postgresql.ENUM(*_EXECUTION_STATUS_VALUES, name=_EXECUTION_STATUS_ENUM_NAME).create(
        op.get_bind(), checkfirst=True
    )

    op.create_table(
        "ejecuciones_ivr",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("id_envio", sa.String(length=64), nullable=False),
        sa.Column(
            "id_campania",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("campanias.id"),
            nullable=False,
        ),
        sa.Column(
            "id_programacion",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("programacion_campanias.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("id_organizacion", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("estado", execution_status, nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("llamadas_por_segundo", sa.Integer(), nullable=True),
        sa.Column("maximo_concurrentes", sa.Integer(), nullable=True),
        sa.Column("despachado_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finalizado_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), nullable=True),
        sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_ejecuciones_ivr_id_envio", "ejecuciones_ivr", ["id_envio"], unique=True
    )
    op.create_index(
        "ix_ejecuciones_ivr_id_campania", "ejecuciones_ivr", ["id_campania"]
    )
    op.create_index(
        "ix_ejecuciones_ivr_id_organizacion", "ejecuciones_ivr", ["id_organizacion"]
    )

    op.add_column(
        "flujos_ivr", sa.Column("llamadas_por_segundo", sa.Integer(), nullable=True)
    )
    op.add_column(
        "flujos_ivr", sa.Column("maximo_concurrentes", sa.Integer(), nullable=True)
    )
    op.add_column(
        "flujos_ivr", sa.Column("id_llamante", sa.String(length=50), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("flujos_ivr", "id_llamante")
    op.drop_column("flujos_ivr", "maximo_concurrentes")
    op.drop_column("flujos_ivr", "llamadas_por_segundo")

    op.drop_index("ix_ejecuciones_ivr_id_organizacion", table_name="ejecuciones_ivr")
    op.drop_index("ix_ejecuciones_ivr_id_campania", table_name="ejecuciones_ivr")
    op.drop_index("ix_ejecuciones_ivr_id_envio", table_name="ejecuciones_ivr")
    op.drop_table("ejecuciones_ivr")

    postgresql.ENUM(*_EXECUTION_STATUS_VALUES, name=_EXECUTION_STATUS_ENUM_NAME).drop(
        op.get_bind(), checkfirst=True
    )
