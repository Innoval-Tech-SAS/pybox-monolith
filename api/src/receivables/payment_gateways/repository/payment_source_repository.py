import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.payment_gateways.enums.payment_gateway_enums import ReceivablesGatewayProvider
from receivables.payment_gateways.models.payment_source_model import DebtorPaymentSourceModel


class DebtorPaymentSourceRepository(SoftDeleteRepositoryBase[DebtorPaymentSourceModel]):
    model_class = DebtorPaymentSourceModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def list_active_by_debtor_id(self, debtor_id: uuid.UUID) -> list[DebtorPaymentSourceModel]:
        result = await self.session.execute(
            select(DebtorPaymentSourceModel).where(
                DebtorPaymentSourceModel.debtor_id == debtor_id,
                DebtorPaymentSourceModel.is_active.is_(True),
                DebtorPaymentSourceModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_active_by_debtor_and_provider(
        self, debtor_id: uuid.UUID, provider: ReceivablesGatewayProvider
    ) -> DebtorPaymentSourceModel | None:
        """La fuente vigente para cobro automático (ver `AutomaticChargeService`): una
        organización cobra siempre con el mismo proveedor, así que basta la más reciente
        activa de ese proveedor para ese deudor."""
        result = await self.session.execute(
            select(DebtorPaymentSourceModel)
            .where(
                DebtorPaymentSourceModel.debtor_id == debtor_id,
                DebtorPaymentSourceModel.provider == provider,
                DebtorPaymentSourceModel.is_active.is_(True),
                DebtorPaymentSourceModel.deleted_at.is_(None),
            )
            .order_by(DebtorPaymentSourceModel.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()
