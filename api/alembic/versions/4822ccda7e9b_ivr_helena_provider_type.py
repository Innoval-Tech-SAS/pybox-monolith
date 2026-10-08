"""Valor HELENA en el enum tipo_proveedor_envio (contactos.proveedor)

Revision ID: 4822ccda7e9b
Revises: b5c6d7e8f9a0
Create Date: 2026-09-14 05:00:00

`ProviderType.HELENA` (api/src/messaging/contacts/enums/contact_enums.py) se usa
para etiquetar en `contactos.proveedor` los envíos del canal de llamadas IVR
(ver `provider_for_channel` en messaging/campaigns/utils/provider_utils.py).
Postgres no altera un tipo ENUM existente por sí solo (ni `Base.metadata.create_all`
ni un `ALTER TABLE` lo hacen): sin esta migración, persistir un contacto de una
campaña de llamadas falla con "invalid input value for enum tipo_proveedor_envio".

NO se ejecuta automáticamente -- generada para ejecución manual por el usuario
(alembic upgrade head).
"""

from typing import Sequence, Union

from alembic import op

revision: str = "4822ccda7e9b"
down_revision: Union[str, None] = "b5c6d7e8f9a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # `ADD VALUE IF NOT EXISTS` es idempotente y, desde PG12, funciona dentro de
    # la transacción de la migración (mismo patrón que e2f3a4b5c6d7_ivr_interactions).
    op.execute("ALTER TYPE tipo_proveedor_envio ADD VALUE IF NOT EXISTS 'HELENA'")


def downgrade() -> None:
    # Postgres no soporta quitar un valor de un ENUM sin recrear el tipo y
    # reescribir la columna. El valor queda como residuo inofensivo si no hay
    # contactos de canal CALL que lo usen; se documenta en vez de hacerlo en silencio.
    pass
