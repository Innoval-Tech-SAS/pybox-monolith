"""Tabla interacciones_ivr + estados de llamada en contactos

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-09-14 00:00:00

Fase 3 del plan `ivr-helena`: ingesta de los resultados que Helena reporta por
webhook. Crea la tabla de interacciones (una por llamada; con remarcación hay
varias por destinatario) y agrega al enum `contactstatus` los dos estados que
describen el resultado de una llamada.

IMPORTANTE: los valores nuevos del enum NO los crea `Base.metadata.create_all`
del arranque -- Postgres no altera un tipo ENUM existente. Esta migración tiene
que correr ANTES de que llegue el primer webhook de Helena, o el guardado del
estado del contacto fallará con "invalid input value for enum contactstatus".

NO se ejecuta automáticamente -- generada para ejecución manual por el usuario
(alembic upgrade head).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e2f3a4b5c6d7"
down_revision: Union[str, None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CALL_STATUS_ENUM_NAME = "ivrcallstatus"
_CALL_STATUS_VALUES = (
    "QUEUED",
    "RINGING",
    "HUMAN_DETECTED",
    "MACHINE_DETECTED",
    "IN_IVR",
    "TRANSFERRING",
    "COMPLETED",
    "NO_ANSWER",
    "FAILED",
    "CANCELLED",
)

_NEW_CONTACT_STATUSES = ("ANSWERED", "NO_ANSWER")


def upgrade() -> None:
    # `create_type=False` es imprescindible: sin él, `op.create_table` vuelve a
    # emitir su propio CREATE TYPE al encontrar la columna que usa este enum y
    # la migración falla con "type ivrcallstatus already exists". El tipo se
    # crea aquí explícitamente, con checkfirst para que sea reejecutable.
    call_status = postgresql.ENUM(
        *_CALL_STATUS_VALUES, name=_CALL_STATUS_ENUM_NAME, create_type=False
    )
    postgresql.ENUM(*_CALL_STATUS_VALUES, name=_CALL_STATUS_ENUM_NAME).create(
        op.get_bind(), checkfirst=True
    )

    op.create_table(
        "interacciones_ivr",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        # Identidad en Helena
        sa.Column("id_interaccion", sa.String(length=64), nullable=False),
        sa.Column("id_envio", sa.String(length=64), nullable=False),
        sa.Column("id_interaccion_raiz", sa.String(length=64), nullable=True),
        sa.Column("numero_intento", sa.Integer(), nullable=False, server_default=sa.text("1")),
        # Correlación con Pybox
        sa.Column(
            "id_contacto",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("contactos.id"),
            nullable=True,
        ),
        sa.Column(
            "id_campania",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("campanias.id"),
            nullable=True,
        ),
        sa.Column("id_organizacion", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "id_deudor",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("deudores.id"),
            nullable=True,
        ),
        # Destinatario
        sa.Column("telefono", sa.String(length=32), nullable=False),
        sa.Column("nombre_cliente", sa.String(length=255), nullable=True),
        sa.Column("documento_cliente", sa.String(length=50), nullable=True),
        # Resultado
        sa.Column("estado", call_status, nullable=False),
        sa.Column("estado_amd", sa.String(length=20), nullable=True),
        sa.Column("causa_amd", sa.String(length=50), nullable=True),
        sa.Column("estado_marcacion", sa.String(length=50), nullable=True),
        sa.Column("nodo_final_ivr", sa.String(length=100), nullable=True),
        sa.Column("razon_final_ivr", sa.String(length=100), nullable=True),
        sa.Column(
            "transferido", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column("estado_transferencia", sa.String(length=50), nullable=True),
        sa.Column("duracion_segundos", sa.Integer(), nullable=True),
        sa.Column("segundos_facturables", sa.Integer(), nullable=True),
        # Interacción con el IVR
        sa.Column("eventos_dtmf", postgresql.JSONB(), nullable=True),
        sa.Column("datos_capturados", postgresql.JSONB(), nullable=True),
        # Ciclo de la llamada
        sa.Column("iniciada_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("contestada_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("transferencia_iniciada_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finalizada_en", sa.DateTime(timezone=True), nullable=True),
        # Trazabilidad
        sa.Column("ultimo_evento", sa.String(length=60), nullable=True),
        sa.Column("payload_crudo", postgresql.JSONB(), nullable=True),
        # Auditoría (AuditModel)
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
        "ix_interacciones_ivr_id_interaccion",
        "interacciones_ivr",
        ["id_interaccion"],
        unique=True,
    )
    op.create_index("ix_interacciones_ivr_id_envio", "interacciones_ivr", ["id_envio"])
    op.create_index(
        "ix_interacciones_ivr_id_interaccion_raiz", "interacciones_ivr", ["id_interaccion_raiz"]
    )
    op.create_index("ix_interacciones_ivr_id_contacto", "interacciones_ivr", ["id_contacto"])
    op.create_index("ix_interacciones_ivr_id_campania", "interacciones_ivr", ["id_campania"])
    op.create_index(
        "ix_interacciones_ivr_id_organizacion", "interacciones_ivr", ["id_organizacion"]
    )
    op.create_index("ix_interacciones_ivr_telefono", "interacciones_ivr", ["telefono"])
    op.create_index(
        "ix_interacciones_ivr_campania_estado", "interacciones_ivr", ["id_campania", "estado"]
    )
    op.create_index(
        "ix_interacciones_ivr_envio_telefono", "interacciones_ivr", ["id_envio", "telefono"]
    )

    # Estados de contacto propios del canal de llamadas. `ADD VALUE IF NOT
    # EXISTS` es idempotente y, desde PG12, funciona dentro de la transacción
    # de la migración.
    for value in _NEW_CONTACT_STATUSES:
        op.execute(f"ALTER TYPE contactstatus ADD VALUE IF NOT EXISTS '{value}'")


def downgrade() -> None:
    op.drop_index("ix_interacciones_ivr_envio_telefono", table_name="interacciones_ivr")
    op.drop_index("ix_interacciones_ivr_campania_estado", table_name="interacciones_ivr")
    op.drop_index("ix_interacciones_ivr_telefono", table_name="interacciones_ivr")
    op.drop_index("ix_interacciones_ivr_id_organizacion", table_name="interacciones_ivr")
    op.drop_index("ix_interacciones_ivr_id_campania", table_name="interacciones_ivr")
    op.drop_index("ix_interacciones_ivr_id_contacto", table_name="interacciones_ivr")
    op.drop_index("ix_interacciones_ivr_id_interaccion_raiz", table_name="interacciones_ivr")
    op.drop_index("ix_interacciones_ivr_id_envio", table_name="interacciones_ivr")
    op.drop_index("ix_interacciones_ivr_id_interaccion", table_name="interacciones_ivr")
    op.drop_table("interacciones_ivr")

    postgresql.ENUM(*_CALL_STATUS_VALUES, name=_CALL_STATUS_ENUM_NAME).drop(
        op.get_bind(), checkfirst=True
    )

    # Postgres no soporta quitar un valor de un ENUM. Para dejar `contactstatus`
    # exactamente como estaba habría que recrear el tipo y reescribir la columna;
    # los dos valores nuevos quedan como residuo inofensivo (ninguna fila los usa
    # tras borrar las interacciones). Se documenta en vez de hacerlo en silencio.
    pass
