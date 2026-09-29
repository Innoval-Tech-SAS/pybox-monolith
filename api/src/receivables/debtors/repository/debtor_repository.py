import uuid
from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app_platform.countries.enums.country_enums import UserDocumentType
from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from receivables.credits.models.credit_model import CreditModel
from receivables.debtors.enums.debtor_enums import DebtorType
from receivables.debtors.models.debtor_model import DebtorModel


class DebtorRepository(SoftDeleteRepositoryBase[DebtorModel]):
    model_class = DebtorModel

    async def list_by_document(
        self, document_type: UserDocumentType, document_number_hash: str
    ) -> list[DebtorModel]:
        """Todas las filas de deudor de una persona (una por empresa donde figura).

        Solo para el autoservicio (scope SELF): el titular ve sus obligaciones en todas
        las empresas. El lado empresa nunca debe usar esto: resuelve por
        ``get_by_document_number`` acotado a su organización.
        """
        result = await self.session.execute(
            select(DebtorModel)
            .where(
                DebtorModel.document_type == document_type,
                DebtorModel.document_number_hash == document_number_hash,
                DebtorModel.deleted_at.is_(None),
            )
            .order_by(DebtorModel.created_at.asc(), DebtorModel.id.asc())
        )
        return list(result.scalars().all())

    async def list_holders_by_document(
        self, document_type: UserDocumentType, document_number_hash: str
    ) -> list[DebtorModel]:
        """Igual que ``list_by_document`` pero solo las filas donde la persona
        figura como titular. La validación de identidad por WhatsApp no aplica a
        los co-deudores."""
        result = await self.session.execute(
            select(DebtorModel)
            .where(
                DebtorModel.document_type == document_type,
                DebtorModel.document_number_hash == document_number_hash,
                DebtorModel.debtor_type == DebtorType.DEBTOR,
                DebtorModel.deleted_at.is_(None),
            )
            .order_by(DebtorModel.created_at.asc(), DebtorModel.id.asc())
        )
        return list(result.scalars().all())

    async def get_by_document_hashes(
        self, organization_id: uuid.UUID, document_number_hashes: list[str]
    ) -> list[DebtorModel]:
        if not document_number_hashes:
            return []
        result = await self.session.execute(
            select(DebtorModel).where(
                DebtorModel.organization_id == organization_id,
                DebtorModel.document_number_hash.in_(document_number_hashes),
                DebtorModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_by_document_number(
        self, organization_id: uuid.UUID, document_number_hash: str
    ) -> DebtorModel | None:
        result = await self.session.execute(
            select(DebtorModel).where(
                DebtorModel.organization_id == organization_id,
                DebtorModel.document_number_hash == document_number_hash,
                DebtorModel.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    async def bulk_upsert_by_document_hash(
        self, organization_id: uuid.UUID, debtors: list[dict]
    ) -> dict[str, uuid.UUID]:
        """Un solo `INSERT ... ON CONFLICT DO UPDATE ... RETURNING` para varios deudores
        a la vez (Fase 4 de la auditoría: N+1 en carga de portafolio), en vez de un
        SELECT+INSERT/UPDATE por cada uno. ``debtors``: dicts con
        document_number/document_number_hash/full_name/document_type/debtor_type
        (nombres de atributo del modelo), todos de la ``organization_id`` dada: el
        conflicto se resuelve por (organización, hash), así una carga nunca toca al
        deudor de otra empresa. Devuelve ``{document_number_hash: id}``.
        Mismo criterio de update que la carga fila por fila: solo full_name y
        document_type se sobrescriben en conflicto -- document_number/debtor_type no,
        para no voltear la identidad del deudor."""
        if not debtors:
            return {}

        table = self.model_class.__table__
        values = [
            {
                "id_organizacion": organization_id,
                "numero_documento": d["document_number"],
                "numero_documento_hash": d["document_number_hash"],
                "nombre_completo": d["full_name"],
                "tipo_documento": d["document_type"],
                "tipo_deudor": d["debtor_type"],
            }
            for d in debtors
        ]
        stmt = pg_insert(table).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=[table.c.id_organizacion, table.c.numero_documento_hash],
            set_={
                "nombre_completo": stmt.excluded.nombre_completo,
                "tipo_documento": stmt.excluded.tipo_documento,
                "fecha_actualizacion": datetime.now(timezone.utc),
            },
        ).returning(table.c.id, table.c.numero_documento_hash)

        result = await self.session.execute(stmt)
        return {row.numero_documento_hash: row.id for row in result}

    async def get_by_ids(self, debtor_ids: list[uuid.UUID]) -> list[DebtorModel]:
        if not debtor_ids:
            return []
        result = await self.session.execute(
            select(DebtorModel).where(
                DebtorModel.id.in_(debtor_ids),
                DebtorModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def list_paginated(
        self,
        page: int,
        page_size: int,
        q: str | None = None,
        portfolio_id: uuid.UUID | None = None,
        sort_by: str = "fullName",
        sort_order: str = "asc",
    ) -> tuple[list[DebtorModel], int]:
        query = select(DebtorModel).where(DebtorModel.deleted_at.is_(None))

        if q is not None:
            pattern = f"%{q}%"
            query = query.where(
                or_(
                    DebtorModel.full_name.ilike(pattern),
                    DebtorModel.document_number.ilike(pattern),
                )
            )

        if portfolio_id is not None:
            query = (
                query.join(
                    CreditModel,
                    or_(
                        CreditModel.debtor_id == DebtorModel.id,
                        CreditModel.codebtor_id == DebtorModel.id,
                    ),
                )
                .where(
                    CreditModel.portfolio_id == portfolio_id,
                    CreditModel.deleted_at.is_(None),
                )
                .distinct()
            )

        _sort_cols = {
            "fullName": DebtorModel.full_name,
            "documentNumber": DebtorModel.document_number,
        }
        sort_col = _sort_cols.get(sort_by, DebtorModel.full_name)
        query = query.order_by(
            sort_col.desc() if sort_order == "desc" else sort_col.asc()
        )

        total: int = (
            await self.session.scalar(
                select(func.count()).select_from(query.subquery())
            )
            or 0
        )

        result = await self.session.execute(
            query.offset((page - 1) * page_size).limit(page_size)
        )
        return list(result.scalars().all()), total

    async def soft_delete_by_organization(
        self, organization_id: uuid.UUID, deleted_at: datetime
    ) -> None:
        """Baja en cascada de los deudores de la organización con el sello de la
        organización."""
        await self.soft_delete_where(
            DebtorModel.organization_id == organization_id, deleted_at=deleted_at
        )

    async def restore_by_organization(
        self, organization_id: uuid.UUID, deleted_at: datetime
    ) -> None:
        """Inverso de ``soft_delete_by_organization``: solo lo que cayó con la
        organización."""
        await self.restore_where(
            DebtorModel.organization_id == organization_id, deleted_at=deleted_at
        )
