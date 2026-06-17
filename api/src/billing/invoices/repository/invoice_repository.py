import uuid
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from billing.invoices.enums.invoice_enums import InvoiceStatus
from billing.invoices.models.invoice_model import InvoiceModel
from identity.organizations.models.organization_model import OrganizationModel


class InvoiceRepository(SoftDeleteRepositoryBase[InvoiceModel]):
    model_class = InvoiceModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_current_by_organization_id(self, organization_id: uuid.UUID) -> InvoiceModel | None:
        result = await self.session.execute(
            select(InvoiceModel)
            .where(InvoiceModel.organization_id == organization_id, InvoiceModel.deleted_at.is_(None))
            .order_by(InvoiceModel.period_year.desc(), InvoiceModel.period_month.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def get_by_id_and_organization_id(
        self, id: uuid.UUID, organization_id: uuid.UUID
    ) -> InvoiceModel | None:
        result = await self.session.execute(
            select(InvoiceModel).where(
                InvoiceModel.id == id,
                InvoiceModel.organization_id == organization_id,
                InvoiceModel.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    async def get_open_by_organization_id(self, organization_id: uuid.UUID) -> InvoiceModel | None:
        """Factura mas reciente en un estado que requiere atencion (no PAID/CANCELLED/DRAFT)."""
        result = await self.session.execute(
            select(InvoiceModel)
            .where(
                InvoiceModel.organization_id == organization_id,
                InvoiceModel.deleted_at.is_(None),
                InvoiceModel.status.in_(
                    [
                        InvoiceStatus.ISSUED,
                        InvoiceStatus.PAYMENT_PENDING,
                        InvoiceStatus.OVERDUE,
                        InvoiceStatus.BLOCKED,
                    ]
                ),
            )
            .order_by(InvoiceModel.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def get_by_period(
        self, organization_id: uuid.UUID, period_year: int, period_month: int
    ) -> InvoiceModel | None:
        result = await self.session.execute(
            select(InvoiceModel).where(
                InvoiceModel.organization_id == organization_id,
                InvoiceModel.period_year == period_year,
                InvoiceModel.period_month == period_month,
                InvoiceModel.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    async def list_by_organization_id(
        self, organization_id: uuid.UUID, page: int, limit: int
    ) -> tuple[list[InvoiceModel], int]:
        base_filter = (
            InvoiceModel.organization_id == organization_id,
            InvoiceModel.deleted_at.is_(None),
        )
        total = await self.session.scalar(
            select(func.count()).select_from(InvoiceModel).where(*base_filter)
        )
        result = await self.session.execute(
            select(InvoiceModel)
            .where(*base_filter)
            .order_by(InvoiceModel.period_year.desc(), InvoiceModel.period_month.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        return list(result.scalars().all()), total or 0

    async def get_by_id_with_organization_name(self, id: uuid.UUID) -> tuple[InvoiceModel, str] | None:
        result = await self.session.execute(
            select(InvoiceModel, OrganizationModel.name)
            .join(OrganizationModel, OrganizationModel.id == InvoiceModel.organization_id)
            .where(InvoiceModel.id == id, InvoiceModel.deleted_at.is_(None))
        )
        return result.first()

    async def list_all_with_organization_name(
        self, page: int, limit: int, organization_id: uuid.UUID | None = None
    ) -> tuple[list[tuple[InvoiceModel, str]], int]:
        filters = [InvoiceModel.deleted_at.is_(None)]
        if organization_id is not None:
            filters.append(InvoiceModel.organization_id == organization_id)

        total = await self.session.scalar(select(func.count()).select_from(InvoiceModel).where(*filters))
        result = await self.session.execute(
            select(InvoiceModel, OrganizationModel.name)
            .join(OrganizationModel, OrganizationModel.id == InvoiceModel.organization_id)
            .where(*filters)
            .order_by(InvoiceModel.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        return list(result.all()), total or 0

    async def mark_overdue(self, now: datetime) -> None:
        await self.session.execute(
            update(InvoiceModel)
            .where(
                InvoiceModel.status == InvoiceStatus.ISSUED,
                InvoiceModel.due_at.is_not(None),
                InvoiceModel.due_at < now,
            )
            .values(status=InvoiceStatus.OVERDUE)
        )

    async def mark_blocked(self, now: datetime) -> None:
        await self.session.execute(
            update(InvoiceModel)
            .where(
                InvoiceModel.status.in_([InvoiceStatus.OVERDUE, InvoiceStatus.PAYMENT_PENDING]),
                InvoiceModel.block_at.is_not(None),
                InvoiceModel.block_at < now,
            )
            .values(status=InvoiceStatus.BLOCKED)
        )
