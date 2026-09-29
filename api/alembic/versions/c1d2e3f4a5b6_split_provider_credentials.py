"""split_provider_credentials

`credenciales_proveedor` mezclaba credenciales de mensajeria (360NRS/WhatsApp) con
credenciales de pasarela de pago (Mercado Pago/Bold) de la propia plataforma. Se separa
en dos tablas segun ese eje:

  * credenciales_mensajeria: NRS360_SMS, NRS360_EMAIL, WHATSAPP_CLOUD (scope pais).
  * credenciales_pasarela_plataforma: MERCADOPAGO, BOLD -- cuenta PROPIA de PYBOX para
    cobrar a las organizaciones (scope pais, igual que antes).

Los datos existentes se redistribuyen por el valor de `proveedor`, sin perdida: la
migracion es reversible (ver downgrade).

Revision ID: c1d2e3f4a5b6
Revises: b7c8d9e0f1a2
Create Date: 2026-09-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, None] = "b7c8d9e0f1a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_MESSAGING_PROVIDERS = ("360NRS_SMS", "360NRS_EMAIL", "WHATSAPP_CLOUD")
_PLATFORM_GATEWAY_PROVIDERS = ("MERCADOPAGO", "BOLD")


def upgrade() -> None:
    sa.Enum(*_MESSAGING_PROVIDERS, name="proveedor_credencial_mensajeria").create(op.get_bind())
    sa.Enum(*_PLATFORM_GATEWAY_PROVIDERS, name="proveedor_pasarela_plataforma").create(op.get_bind())

    op.create_table(
        "credenciales_mensajeria",
        sa.Column("codigo_pais", sa.String(length=2), nullable=True),
        sa.Column("proveedor", postgresql.ENUM(*_MESSAGING_PROVIDERS, name="proveedor_credencial_mensajeria", create_type=False), nullable=False),
        sa.Column("secretos", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("config_publica", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("clave_busqueda", sa.String(length=255), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), nullable=True),
        sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["codigo_pais"], ["paises.codigo"], name=op.f("fk_credenciales_mensajeria_codigo_pais_paises")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_credenciales_mensajeria")),
    )
    op.create_index(op.f("ix_credenciales_mensajeria_clave_busqueda"), "credenciales_mensajeria", ["clave_busqueda"], unique=False)
    op.create_index(
        "uq_credencial_mensajeria_pais_proveedor", "credenciales_mensajeria", ["codigo_pais", "proveedor"],
        unique=True, postgresql_where=sa.text("eliminado_en IS NULL"),
    )

    op.create_table(
        "credenciales_pasarela_plataforma",
        sa.Column("codigo_pais", sa.String(length=2), nullable=True),
        sa.Column("proveedor", postgresql.ENUM(*_PLATFORM_GATEWAY_PROVIDERS, name="proveedor_pasarela_plataforma", create_type=False), nullable=False),
        sa.Column("secretos", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("config_publica", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("clave_busqueda", sa.String(length=255), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), nullable=True),
        sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["codigo_pais"], ["paises.codigo"], name=op.f("fk_credenciales_pasarela_plataforma_codigo_pais_paises")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_credenciales_pasarela_plataforma")),
    )
    op.create_index(op.f("ix_credenciales_pasarela_plataforma_clave_busqueda"), "credenciales_pasarela_plataforma", ["clave_busqueda"], unique=False)
    op.create_index(
        "uq_credencial_pasarela_plataforma_pais_proveedor", "credenciales_pasarela_plataforma", ["codigo_pais", "proveedor"],
        unique=True, postgresql_where=sa.text("eliminado_en IS NULL"),
    )

    # Redistribucion de los datos existentes segun el valor de `proveedor`. El cast
    # `::text::<nuevo_enum>` es necesario porque, aunque los valores coinciden, son tipos
    # ENUM distintos para Postgres.
    op.execute(
        f"""
        INSERT INTO credenciales_mensajeria (
            codigo_pais, proveedor, secretos, config_publica, clave_busqueda, activo,
            id, fecha_creacion, fecha_actualizacion, eliminado_en
        )
        SELECT codigo_pais, proveedor::text::proveedor_credencial_mensajeria, secretos, config_publica,
               clave_busqueda, activo, id, fecha_creacion, fecha_actualizacion, eliminado_en
        FROM credenciales_proveedor
        WHERE proveedor::text IN {_MESSAGING_PROVIDERS!r}
        """
    )
    op.execute(
        f"""
        INSERT INTO credenciales_pasarela_plataforma (
            codigo_pais, proveedor, secretos, config_publica, clave_busqueda, activo,
            id, fecha_creacion, fecha_actualizacion, eliminado_en
        )
        SELECT codigo_pais, proveedor::text::proveedor_pasarela_plataforma, secretos, config_publica,
               clave_busqueda, activo, id, fecha_creacion, fecha_actualizacion, eliminado_en
        FROM credenciales_proveedor
        WHERE proveedor::text IN {_PLATFORM_GATEWAY_PROVIDERS!r}
        """
    )

    op.drop_index("uq_credencial_pais_proveedor", table_name="credenciales_proveedor", postgresql_where=sa.text("eliminado_en IS NULL"))
    op.drop_index(op.f("ix_credenciales_proveedor_clave_busqueda"), table_name="credenciales_proveedor")
    op.drop_table("credenciales_proveedor")
    sa.Enum(*_MESSAGING_PROVIDERS, *_PLATFORM_GATEWAY_PROVIDERS, name="proveedor_credencial").drop(op.get_bind())


def downgrade() -> None:
    sa.Enum(*_MESSAGING_PROVIDERS, *_PLATFORM_GATEWAY_PROVIDERS, name="proveedor_credencial").create(op.get_bind())
    op.create_table(
        "credenciales_proveedor",
        sa.Column("codigo_pais", sa.String(length=2), nullable=True),
        sa.Column("proveedor", postgresql.ENUM(*_MESSAGING_PROVIDERS, *_PLATFORM_GATEWAY_PROVIDERS, name="proveedor_credencial", create_type=False), nullable=False),
        sa.Column("secretos", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("config_publica", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("clave_busqueda", sa.String(length=255), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), nullable=True),
        sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["codigo_pais"], ["paises.codigo"], name=op.f("fk_credenciales_proveedor_codigo_pais_paises")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_credenciales_proveedor")),
    )
    op.create_index(op.f("ix_credenciales_proveedor_clave_busqueda"), "credenciales_proveedor", ["clave_busqueda"], unique=False)
    op.create_index(
        "uq_credencial_pais_proveedor", "credenciales_proveedor", ["codigo_pais", "proveedor"],
        unique=True, postgresql_where=sa.text("eliminado_en IS NULL"),
    )

    op.execute(
        """
        INSERT INTO credenciales_proveedor (
            codigo_pais, proveedor, secretos, config_publica, clave_busqueda, activo,
            id, fecha_creacion, fecha_actualizacion, eliminado_en
        )
        SELECT codigo_pais, proveedor::text::proveedor_credencial, secretos, config_publica,
               clave_busqueda, activo, id, fecha_creacion, fecha_actualizacion, eliminado_en
        FROM credenciales_mensajeria
        UNION ALL
        SELECT codigo_pais, proveedor::text::proveedor_credencial, secretos, config_publica,
               clave_busqueda, activo, id, fecha_creacion, fecha_actualizacion, eliminado_en
        FROM credenciales_pasarela_plataforma
        """
    )

    op.drop_index("uq_credencial_pasarela_plataforma_pais_proveedor", table_name="credenciales_pasarela_plataforma", postgresql_where=sa.text("eliminado_en IS NULL"))
    op.drop_index(op.f("ix_credenciales_pasarela_plataforma_clave_busqueda"), table_name="credenciales_pasarela_plataforma")
    op.drop_table("credenciales_pasarela_plataforma")
    sa.Enum(*_PLATFORM_GATEWAY_PROVIDERS, name="proveedor_pasarela_plataforma").drop(op.get_bind())

    op.drop_index("uq_credencial_mensajeria_pais_proveedor", table_name="credenciales_mensajeria", postgresql_where=sa.text("eliminado_en IS NULL"))
    op.drop_index(op.f("ix_credenciales_mensajeria_clave_busqueda"), table_name="credenciales_mensajeria")
    op.drop_table("credenciales_mensajeria")
    sa.Enum(*_MESSAGING_PROVIDERS, name="proveedor_credencial_mensajeria").drop(op.get_bind())
