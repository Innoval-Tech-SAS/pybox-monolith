"""debtors_scoped_to_organization

El deudor pasa de ser global (unique por hash de documento) a pertenecer a una
organización (unique por organización + hash de documento).

Backfill de los datos existentes:
  * La organización de un deudor se deduce de sus créditos (titular o codeudor) vía
    portafolio.
  * Si un mismo deudor tenía créditos en varias organizaciones, se conserva la fila
    original para la primera organización y se clona para cada una de las demás; los
    créditos, extractos, contactos, chats y demás filas con organización se reapuntan
    al clon de su organización. Direcciones y métodos de contacto se copian (antes eran
    compartidos); los documentos del deudor quedan con la fila original.
  * Los deudores sin ningún crédito no son alcanzables desde ninguna organización: se
    eliminan junto con sus direcciones, métodos de contacto y enlaces a documentos.

Revision ID: b7c8d9e0f1a2
Revises: 98ae961d8224
Create Date: 2026-09-23 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, None] = "98ae961d8224"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Tablas (distintas de `creditos`) con `id_organizacion` + `id_deudor`: al clonar un
# deudor se reapuntan a la copia de su propia organización.
_TABLES_WITH_ORG_AND_DEBTOR = (
    "extractos",
    "contactos",
    "interacciones_ivr",
    "solicitudes_canal_whatsapp",
    "whatsapp_chats",
)


def upgrade() -> None:
    op.add_column(
        "deudores",
        sa.Column("id_organizacion", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # (deudor, organización) según sus créditos, con rn = 1 para la organización que
    # conserva la fila original.
    op.execute("""
        CREATE TEMP TABLE _deudor_org ON COMMIT DROP AS
        SELECT d_id, org, row_number() OVER (PARTITION BY d_id ORDER BY org) AS rn
        FROM (
            SELECT c.id_deudor AS d_id, p.id_organizacion AS org
            FROM creditos c JOIN portafolios p ON p.id = c.id_portafolio
            UNION
            SELECT c.id_codeudor, p.id_organizacion
            FROM creditos c JOIN portafolios p ON p.id = c.id_portafolio
            WHERE c.id_codeudor IS NOT NULL
        ) t
        """)
    op.execute(
        "UPDATE deudores d SET id_organizacion = t.org FROM _deudor_org t WHERE t.d_id = d.id AND t.rn = 1"
    )

    # Clones para las organizaciones adicionales.
    op.execute("""
        CREATE TEMP TABLE _clon ON COMMIT DROP AS
        SELECT d_id, org, gen_random_uuid() AS new_id FROM _deudor_org WHERE rn > 1
        """)
    op.execute("""
        INSERT INTO deudores (
            id, nombre_completo, tipo_deudor, tipo_documento, numero_documento,
            numero_documento_hash, fecha_creacion, fecha_actualizacion, eliminado_en, id_organizacion
        )
        SELECT c.new_id, d.nombre_completo, d.tipo_deudor, d.tipo_documento, d.numero_documento,
               d.numero_documento_hash, d.fecha_creacion, d.fecha_actualizacion, d.eliminado_en, c.org
        FROM _clon c JOIN deudores d ON d.id = c.d_id
        """)
    op.execute("""
        UPDATE creditos cr SET id_deudor = c.new_id
        FROM _clon c, portafolios p
        WHERE cr.id_deudor = c.d_id AND p.id = cr.id_portafolio AND p.id_organizacion = c.org
        """)
    op.execute("""
        UPDATE creditos cr SET id_codeudor = c.new_id
        FROM _clon c, portafolios p
        WHERE cr.id_codeudor = c.d_id AND p.id = cr.id_portafolio AND p.id_organizacion = c.org
        """)
    for table in _TABLES_WITH_ORG_AND_DEBTOR:
        op.execute(
            f"UPDATE {table} t SET id_deudor = c.new_id "
            f"FROM _clon c WHERE t.id_deudor = c.d_id AND t.id_organizacion = c.org"
        )
    op.execute("""
        INSERT INTO direcciones (
            id, direccion, ciudad, departamento, pais, tipo_direccion, id_deudor,
            fecha_creacion, fecha_actualizacion, eliminado_en
        )
        SELECT gen_random_uuid(), a.direccion, a.ciudad, a.departamento, a.pais, a.tipo_direccion, c.new_id,
               a.fecha_creacion, a.fecha_actualizacion, a.eliminado_en
        FROM direcciones a JOIN _clon c ON c.d_id = a.id_deudor
        """)
    op.execute("""
        INSERT INTO metodos_contacto (
            id, tipo_metodo_contacto, metodo_contacto, id_deudor,
            fecha_creacion, fecha_actualizacion, eliminado_en
        )
        SELECT gen_random_uuid(), m.tipo_metodo_contacto, m.metodo_contacto, c.new_id,
               m.fecha_creacion, m.fecha_actualizacion, m.eliminado_en
        FROM metodos_contacto m JOIN _clon c ON c.d_id = m.id_deudor
        """)

    # Deudores sin créditos: inalcanzables desde cualquier organización.
    op.execute(
        "DELETE FROM direcciones WHERE id_deudor IN (SELECT id FROM deudores WHERE id_organizacion IS NULL)"
    )
    op.execute(
        "DELETE FROM metodos_contacto WHERE id_deudor IN (SELECT id FROM deudores WHERE id_organizacion IS NULL)"
    )
    op.execute(
        "DELETE FROM documentos_deudor WHERE id_deudor IN (SELECT id FROM deudores WHERE id_organizacion IS NULL)"
    )
    op.execute("DELETE FROM deudores WHERE id_organizacion IS NULL")

    op.alter_column("deudores", "id_organizacion", nullable=False)
    op.create_foreign_key(
        op.f("fk_deudores_id_organizacion_entidades"),
        "deudores",
        "entidades",
        ["id_organizacion"],
        ["id"],
    )
    op.create_index(
        op.f("ix_deudores_id_organizacion"),
        "deudores",
        ["id_organizacion"],
        unique=False,
    )
    op.drop_index(op.f("ix_deudores_numero_documento_hash"), table_name="deudores")
    op.create_index(
        op.f("ix_deudores_numero_documento_hash"),
        "deudores",
        ["numero_documento_hash"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_deudores_organizacion_documento",
        "deudores",
        ["id_organizacion", "numero_documento_hash"],
    )


def downgrade() -> None:
    # No hay forma segura de volver a unir los deudores que se clonaron por organización:
    # el downgrade falla si el mismo documento existe en más de una organización.
    op.drop_constraint("uq_deudores_organizacion_documento", "deudores", type_="unique")
    op.drop_index(op.f("ix_deudores_numero_documento_hash"), table_name="deudores")
    op.create_index(
        op.f("ix_deudores_numero_documento_hash"),
        "deudores",
        ["numero_documento_hash"],
        unique=True,
    )
    op.drop_index(op.f("ix_deudores_id_organizacion"), table_name="deudores")
    op.drop_constraint(
        op.f("fk_deudores_id_organizacion_entidades"), "deudores", type_="foreignkey"
    )
    op.drop_column("deudores", "id_organizacion")
