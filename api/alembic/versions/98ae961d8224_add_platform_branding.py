"""add_platform_branding

Revision ID: 98ae961d8224
Revises: a1b2c3d4e5f6
Create Date: 2026-09-16 23:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '98ae961d8224'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'configuracion_plataforma',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('eliminado_en', sa.DateTime(timezone=True), nullable=True),
        sa.Column('clave_singleton', sa.SmallInteger(), nullable=False),
        sa.Column('id_documento_logo', postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint('clave_singleton = 1', name='ck_configuracion_plataforma_singleton'),
        sa.ForeignKeyConstraint(['id_documento_logo'], ['documentos.id'], name='fk_configuracion_plataforma_id_documento_logo_documentos', use_alter=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('clave_singleton'),
    )
    # Fila única desde el día uno: el repo nunca necesita "crear si no existe".
    op.execute("INSERT INTO configuracion_plataforma (id, clave_singleton) VALUES (gen_random_uuid(), 1)")


def downgrade() -> None:
    op.drop_table('configuracion_plataforma')
