"""credit_payment_gateway_tables

Tablas nuevas para el cobro de cuotas de cartera (deudor -> empresa) vía la pasarela
propia de la organización (ver skill `wompi-gateway`):

- `fuentes_pago_deudor`: medio de pago tokenizado y reutilizable de un deudor (tarjeta o
  Nequi), para cobro recurrente sin que reingrese sus datos.
- `intentos_pago_credito`: log de intentos de cobro contra una cuota (`pagos`), clon de
  `intentos_pago_factura` — incluye intentos fallidos (DECLINED/ERROR/VOIDED), no solo
  los que terminan pagados.

`fuentes_pago_deudor` se crea primero porque `intentos_pago_credito.id_fuente_pago` la
referencia (cobro AUTOMATIC_3RI contra una fuente guardada).

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-09-28 13:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_ORG_GATEWAY_PROVIDERS = ("WOMPI", "BOLD", "PAYU", "EPAYCO")
_PAYMENT_SOURCE_TYPES = ("CARD", "NEQUI")
_PAYMENT_SOURCE_STATUSES = ("PENDING", "AVAILABLE", "DECLINED", "ERROR")
_ATTEMPT_STATUSES = ("PENDING", "APPROVED", "DECLINED", "ERROR", "VOIDED")
_CHARGE_MODES = ("CHECKOUT", "AUTOMATIC_3RI")


def upgrade() -> None:
    sa.Enum(*_PAYMENT_SOURCE_TYPES, name="tipo_fuente_pago").create(op.get_bind())
    sa.Enum(*_PAYMENT_SOURCE_STATUSES, name="estado_fuente_pago").create(op.get_bind())
    sa.Enum(*_ATTEMPT_STATUSES, name="estado_intento_pago_credito").create(
        op.get_bind()
    )
    sa.Enum(*_CHARGE_MODES, name="modo_cobro").create(op.get_bind())

    op.create_table(
        "fuentes_pago_deudor",
        sa.Column("id_deudor", sa.UUID(), nullable=False),
        sa.Column(
            "proveedor",
            postgresql.ENUM(
                *_ORG_GATEWAY_PROVIDERS,
                name="proveedor_pasarela_organizacion",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "tipo",
            postgresql.ENUM(
                *_PAYMENT_SOURCE_TYPES, name="tipo_fuente_pago", create_type=False
            ),
            nullable=False,
        ),
        sa.Column("id_fuente_proveedor", sa.String(length=255), nullable=False),
        sa.Column(
            "estado",
            postgresql.ENUM(
                *_PAYMENT_SOURCE_STATUSES, name="estado_fuente_pago", create_type=False
            ),
            nullable=False,
        ),
        sa.Column("inscrito_3ds", sa.Boolean(), nullable=False),
        sa.Column("identificador_enmascarado", sa.String(length=40), nullable=True),
        sa.Column("marca", sa.String(length=40), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("fecha_aceptacion", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), nullable=True),
        sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["id_deudor"],
            ["deudores.id"],
            name=op.f("fk_fuentes_pago_deudor_id_deudor_deudores"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_fuentes_pago_deudor")),
    )
    op.create_index(
        op.f("ix_fuentes_pago_deudor_id_deudor"),
        "fuentes_pago_deudor",
        ["id_deudor"],
        unique=False,
    )
    op.create_index(
        op.f("ix_fuentes_pago_deudor_id_fuente_proveedor"),
        "fuentes_pago_deudor",
        ["id_fuente_proveedor"],
        unique=False,
    )

    op.create_table(
        "intentos_pago_credito",
        sa.Column("id_pago", sa.UUID(), nullable=False),
        sa.Column("numero_intento", sa.Integer(), nullable=False),
        sa.Column(
            "proveedor",
            postgresql.ENUM(
                *_ORG_GATEWAY_PROVIDERS,
                name="proveedor_pasarela_organizacion",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "modo_cobro",
            postgresql.ENUM(*_CHARGE_MODES, name="modo_cobro", create_type=False),
            nullable=False,
        ),
        sa.Column("referencia_proveedor", sa.String(length=60), nullable=True),
        sa.Column("id_transaccion_proveedor", sa.String(length=255), nullable=True),
        sa.Column("id_fuente_pago", sa.UUID(), nullable=True),
        sa.Column("monto_esperado_centavos", sa.BigInteger(), nullable=True),
        sa.Column(
            "estado",
            postgresql.ENUM(
                *_ATTEMPT_STATUSES,
                name="estado_intento_pago_credito",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "payload_proveedor", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("permalink_aceptacion", sa.String(length=500), nullable=True),
        sa.Column("permalink_datos_personales", sa.String(length=500), nullable=True),
        sa.Column("fecha_aceptacion", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), nullable=True),
        sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["id_pago"],
            ["pagos.id"],
            name=op.f("fk_intentos_pago_credito_id_pago_pagos"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["id_fuente_pago"],
            ["fuentes_pago_deudor.id"],
            name=op.f("fk_intentos_pago_credito_id_fuente_pago_fuentes_pago_deudor"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_intentos_pago_credito")),
    )
    op.create_index(
        op.f("ix_intentos_pago_credito_id_pago"),
        "intentos_pago_credito",
        ["id_pago"],
        unique=False,
    )
    op.create_index(
        op.f("ix_intentos_pago_credito_referencia_proveedor"),
        "intentos_pago_credito",
        ["referencia_proveedor"],
        unique=False,
    )
    op.create_index(
        op.f("ix_intentos_pago_credito_id_transaccion_proveedor"),
        "intentos_pago_credito",
        ["id_transaccion_proveedor"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_intentos_pago_credito_id_transaccion_proveedor"),
        table_name="intentos_pago_credito",
    )
    op.drop_index(
        op.f("ix_intentos_pago_credito_referencia_proveedor"),
        table_name="intentos_pago_credito",
    )
    op.drop_index(
        op.f("ix_intentos_pago_credito_id_pago"), table_name="intentos_pago_credito"
    )
    op.drop_table("intentos_pago_credito")

    op.drop_index(
        op.f("ix_fuentes_pago_deudor_id_fuente_proveedor"),
        table_name="fuentes_pago_deudor",
    )
    op.drop_index(
        op.f("ix_fuentes_pago_deudor_id_deudor"), table_name="fuentes_pago_deudor"
    )
    op.drop_table("fuentes_pago_deudor")

    sa.Enum(*_CHARGE_MODES, name="modo_cobro").drop(op.get_bind())
    sa.Enum(*_ATTEMPT_STATUSES, name="estado_intento_pago_credito").drop(op.get_bind())
    sa.Enum(*_PAYMENT_SOURCE_STATUSES, name="estado_fuente_pago").drop(op.get_bind())
    sa.Enum(*_PAYMENT_SOURCE_TYPES, name="tipo_fuente_pago").drop(op.get_bind())
