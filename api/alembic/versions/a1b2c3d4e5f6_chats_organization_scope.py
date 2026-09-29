"""chats: columna organization_id para fijar el scope de un grupo

Revision ID: a1b2c3d4e5f6
Revises: 4822ccda7e9b
Create Date: 2026-09-16 00:00:00

Los chats grupales (`chats.tipo = GROUP`) pueden ser "global-only" (todos los
miembros son usuarios GLOBAL-scope) u "org-scoped" (miembros de una única
organización + opcionalmente GLOBAL). `id_organizacion` fija ese scope la
primera vez que un miembro ORGANIZATION-scoped entra al grupo -- desde ahí es
inmutable a nivel de aplicación (ver `ChatService._resolve_pinned_organization`).
NULL = grupo global-only o chat DIRECT (esta columna no aplica a DIRECT).

No hay ciclo de FK: `entidades` no referencia `chats`, así que no hace falta
`use_alter=True` aquí (a diferencia de `fk_entidades_id_documento_logo_documentos`).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "4822ccda7e9b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "chats",
        sa.Column("id_organizacion", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        op.f("ix_chats_id_organizacion"), "chats", ["id_organizacion"], unique=False
    )
    op.create_foreign_key(
        "fk_chats_id_organizacion_entidades",
        "chats",
        "entidades",
        ["id_organizacion"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_chats_id_organizacion_entidades", "chats", type_="foreignkey"
    )
    op.drop_index(op.f("ix_chats_id_organizacion"), table_name="chats")
    op.drop_column("chats", "id_organizacion")
