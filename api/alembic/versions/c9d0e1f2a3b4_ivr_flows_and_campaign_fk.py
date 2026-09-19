"""IVR flows table (flujos_ivr) + FK id_flujo_ivr en campanias

Revision ID: c9d0e1f2a3b4
Revises: 0b2714227764
Create Date: 2026-07-14 00:00:00

Integración del canal IVR (Helena). Crea la tabla de flujos IVR reutilizables
y agrega la referencia opcional desde las campañas.

Re-encadenada sobre `0b2714227764` (head de master) al fusionar dev-refactor:
`b7c8d9e0f1a2` (collapse_user_organization_role) fue eliminada porque su
resultado ya quedó incorporado en el baseline consolidado `00f053faf300`.

NO se ejecuta automáticamente -- generada para revisión y ejecución manual por
el usuario (alembic upgrade head).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c9d0e1f2a3b4"
down_revision: Union[str, None] = "0b2714227764"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "flujos_ivr",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "id_portafolio",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("portafolios.id"),
            nullable=False,
        ),
        sa.Column("nombre", sa.String(length=255), nullable=False),
        sa.Column("descripcion", sa.String(length=255), nullable=True),
        sa.Column("config", postgresql.JSONB(), nullable=False),
        sa.Column("grafo", postgresql.JSONB(), nullable=True),
        sa.Column("config_remarcado", postgresql.JSONB(), nullable=True),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), nullable=True),
        sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_flujos_ivr_id_portafolio", "flujos_ivr", ["id_portafolio"])

    op.add_column(
        "campanias",
        sa.Column("id_flujo_ivr", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_campanias_id_flujo_ivr",
        "campanias",
        "flujos_ivr",
        ["id_flujo_ivr"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_campanias_id_flujo_ivr", "campanias", type_="foreignkey")
    op.drop_column("campanias", "id_flujo_ivr")
    op.drop_index("ix_flujos_ivr_id_portafolio", table_name="flujos_ivr")
    op.drop_table("flujos_ivr")
