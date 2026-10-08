"""Repository mixin de resolución país→global para credenciales cifradas."""

from typing import Generic, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

ModelT = TypeVar("ModelT", bound=DeclarativeBase)
ProviderT = TypeVar("ProviderT")


class CountryScopedCredentialRepositoryMixin(Generic[ModelT, ProviderT]):
    """Resolución país→global para credenciales de alcance `country_code` (NULL =
    credencial global): compartida por `billing.provider_credentials` y
    `messaging.provider_credentials`. No aplica a `receivables.payment_gateways`,
    donde `organization_id` es obligatorio y no existe el concepto de credencial
    global — ese repository no usa este mixin."""

    model_class: Type[ModelT]
    session: AsyncSession

    async def get(
        self, country_code: Optional[str], provider: ProviderT
    ) -> Optional[ModelT]:
        country_column = self.model_class.country_code  # type: ignore[attr-defined]
        scope_filter = (
            country_column == country_code
            if country_code is not None
            else country_column.is_(None)
        )
        stmt = select(self.model_class).where(
            self.model_class.provider == provider,  # type: ignore[attr-defined]
            scope_filter,
            self.model_class.deleted_at.is_(None),  # type: ignore[attr-defined]
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def resolve(
        self, country_code: Optional[str], provider: ProviderT
    ) -> Optional[ModelT]:
        """Credencial específica del país; si no existe, cae a la global (país NULL)."""
        if country_code is not None:
            specific = await self.get(country_code, provider)
            if specific is not None:
                return specific
        return await self.get(None, provider)

    async def get_by_lookup_key(
        self, provider: ProviderT, lookup_key: str
    ) -> Optional[ModelT]:
        result = await self.session.execute(
            select(self.model_class).where(
                self.model_class.provider == provider,  # type: ignore[attr-defined]
                self.model_class.lookup_key == lookup_key,  # type: ignore[attr-defined]
                self.model_class.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[ModelT]:
        result = await self.session.execute(
            select(self.model_class).where(
                self.model_class.deleted_at.is_(None)  # type: ignore[attr-defined]
            )
        )
        return list(result.scalars().all())
