"""rename_invoice_payment_attempts

Renombra `intentos_pago` -> `intentos_pago_factura` (clase `PaymentAttemptModel` ->
`InvoicePaymentAttemptModel`). El nombre anterior no distinguia de que era el intento;
antes de agregar `intentos_pago_credito` (cartera, ver siguiente revision) hacia falta
que ambos digan explicitamente a que dominio pertenecen. No hay datos reales en
produccion todavia, asi que no hace falta preservar nada mas que el rename.

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-09-28 13:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_OLD_TABLE = "intentos_pago"
_NEW_TABLE = "intentos_pago_factura"


def upgrade() -> None:
    op.rename_table(_OLD_TABLE, _NEW_TABLE)
    op.execute(
        f'ALTER TABLE "{_NEW_TABLE}" RENAME CONSTRAINT "pk_{_OLD_TABLE}" TO "pk_{_NEW_TABLE}"'
    )
    op.execute(
        f'ALTER TABLE "{_NEW_TABLE}" RENAME CONSTRAINT '
        f'"fk_{_OLD_TABLE}_factura_id_facturas" TO "fk_{_NEW_TABLE}_factura_id_facturas"'
    )
    op.execute(
        f'ALTER INDEX "ix_{_OLD_TABLE}_factura_id" RENAME TO "ix_{_NEW_TABLE}_factura_id"'
    )
    op.execute(
        f'ALTER INDEX "ix_{_OLD_TABLE}_referencia_proveedor" RENAME TO "ix_{_NEW_TABLE}_referencia_proveedor"'
    )


def downgrade() -> None:
    op.execute(
        f'ALTER INDEX "ix_{_NEW_TABLE}_referencia_proveedor" RENAME TO "ix_{_OLD_TABLE}_referencia_proveedor"'
    )
    op.execute(
        f'ALTER INDEX "ix_{_NEW_TABLE}_factura_id" RENAME TO "ix_{_OLD_TABLE}_factura_id"'
    )
    op.execute(
        f'ALTER TABLE "{_NEW_TABLE}" RENAME CONSTRAINT '
        f'"fk_{_NEW_TABLE}_factura_id_facturas" TO "fk_{_OLD_TABLE}_factura_id_facturas"'
    )
    op.execute(
        f'ALTER TABLE "{_NEW_TABLE}" RENAME CONSTRAINT "pk_{_NEW_TABLE}" TO "pk_{_OLD_TABLE}"'
    )
    op.rename_table(_NEW_TABLE, _OLD_TABLE)
