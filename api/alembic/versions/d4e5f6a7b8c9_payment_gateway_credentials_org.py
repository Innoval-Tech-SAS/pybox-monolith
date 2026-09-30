"""payment_gateway_credentials_org

Cada organizacion puede conectar su propia cuenta de pasarela de pago (Wompi, Bold,
PayU, Epayco) para cobrarle a sus deudores. A diferencia de `credenciales_pasarela_plataforma`
(cuenta PROPIA de PYBOX, scope pais), esta tabla es scope organizacion obligatorio: no
existe fila "global". Nace vacia, no hay datos que migrar.

Revision ID: d4e5f6a7b8c9
Revises: c1d2e3f4a5b6
Create Date: 2026-09-28 12:05:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_ORG_GATEWAY_PROVIDERS = ("WOMPI", "BOLD", "PAYU", "EPAYCO")


def upgrade() -> None:
    sa.Enum(*_ORG_GATEWAY_PROVIDERS, name="proveedor_pasarela_organizacion").create(
        op.get_bind()
    )

    op.create_table(
        "credenciales_pasarela_organizacion",
        sa.Column("id_organizacion", sa.UUID(), nullable=False),
        sa.Column(
            "proveedor",
            postgresql.ENUM(
                *_ORG_GATEWAY_PROVIDERS,
                name="proveedor_pasarela_organizacion",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("secretos", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "config_publica", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("clave_busqueda", sa.String(length=255), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), nullable=True),
        sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["id_organizacion"],
            ["entidades.id"],
            name=op.f(
                "fk_credenciales_pasarela_organizacion_id_organizacion_entidades"
            ),
        ),
        sa.PrimaryKeyConstraint(
            "id", name=op.f("pk_credenciales_pasarela_organizacion")
        ),
    )
    op.create_index(
        op.f("ix_credenciales_pasarela_organizacion_id_organizacion"),
        "credenciales_pasarela_organizacion",
        ["id_organizacion"],
        unique=False,
    )
    op.create_index(
        op.f("ix_credenciales_pasarela_organizacion_clave_busqueda"),
        "credenciales_pasarela_organizacion",
        ["clave_busqueda"],
        unique=False,
    )
    op.create_index(
        "uq_credencial_pasarela_organizacion_org_proveedor",
        "credenciales_pasarela_organizacion",
        ["id_organizacion", "proveedor"],
        unique=True,
        postgresql_where=sa.text("eliminado_en IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_credencial_pasarela_organizacion_org_proveedor",
        table_name="credenciales_pasarela_organizacion",
        postgresql_where=sa.text("eliminado_en IS NULL"),
    )
    op.drop_index(
        op.f("ix_credenciales_pasarela_organizacion_clave_busqueda"),
        table_name="credenciales_pasarela_organizacion",
    )
    op.drop_index(
        op.f("ix_credenciales_pasarela_organizacion_id_organizacion"),
        table_name="credenciales_pasarela_organizacion",
    )
    op.drop_table("credenciales_pasarela_organizacion")
    sa.Enum(*_ORG_GATEWAY_PROVIDERS, name="proveedor_pasarela_organizacion").drop(
        op.get_bind()
    )
