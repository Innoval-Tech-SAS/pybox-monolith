from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from app_platform.countries.enums.country_enums import DocumentScope
from app_platform.countries.models.country_document_type_model import CountryDocumentTypeModel
from app_platform.countries.models.country_model import CountryModel
from app_platform.countries.models.document_type_model import DocumentTypeModel


class CountryRepository(SoftDeleteRepositoryBase[CountryModel]):
    model_class = CountryModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def list_active(self) -> list[CountryModel]:
        result = await self.session.execute(
            select(CountryModel)
            .where(CountryModel.is_active.is_(True))
            .order_by(CountryModel.name)
        )
        return list(result.scalars().all())

    async def get_by_code(self, code: str) -> CountryModel | None:
        return await self.session.get(CountryModel, code)

    async def get_active_map(self) -> dict[str, CountryModel]:
        """`{codigo: CountryModel}` de los países activos — para loops (schedulers,
        facturación) que hoy iteran el enum, sin hacer N+1."""
        return {country.code: country for country in await self.list_active()}

    async def get_currency_code(self, country_code: str | None, default: str = "COP") -> str:
        if not country_code:
            return default
        country = await self.get_by_code(country_code)
        return country.currency_code if country else default

    async def get_timezone(self, country_code: str | None, default: str = "UTC") -> str:
        if not country_code:
            return default
        country = await self.get_by_code(country_code)
        return country.timezone if country else default

    async def get_phone_prefix(self, country_code: str | None) -> str | None:
        if not country_code:
            return None
        country = await self.get_by_code(country_code)
        return country.phone_prefix if country else None

    async def list_document_codes_for_country(
        self, country_code: str, scope: DocumentScope
    ) -> list[str]:
        result = await self.session.execute(
            select(CountryDocumentTypeModel.document_code).where(
                CountryDocumentTypeModel.country_code == country_code,
                CountryDocumentTypeModel.scope == scope,
            )
        )
        return list(result.scalars().all())

    async def get_document_labels(self) -> dict[str, str]:
        """`{codigo: etiqueta}` de todo el catálogo de tipos de documento."""
        result = await self.session.execute(
            select(DocumentTypeModel.code, DocumentTypeModel.label)
        )
        return {code: label for code, label in result.all()}

    async def list_document_map(self, scope: DocumentScope) -> dict[str, list[str]]:
        """`{codigo_pais: [codigo_documento, ...]}` para un alcance dado — en una sola
        query, evitando N+1 al armar la respuesta de todos los países."""
        result = await self.session.execute(
            select(
                CountryDocumentTypeModel.country_code,
                CountryDocumentTypeModel.document_code,
            ).where(CountryDocumentTypeModel.scope == scope)
        )
        mapping: dict[str, list[str]] = {}
        for country_code, document_code in result.all():
            mapping.setdefault(country_code, []).append(document_code)
        return mapping

    async def get_document_code(self, country_code: str, scope: DocumentScope) -> str | None:
        """Primer (y único, para fiscal/mercantil) código de documento de un país en
        un alcance dado. Reemplaza a ORG_FISCAL/MERCANTILE_DOCUMENT_BY_NATIONALITY."""
        codes = await self.list_document_codes_for_country(country_code, scope)
        return codes[0] if codes else None

    async def is_document_valid_for_country(
        self, country_code: str, document_code: str, scope: DocumentScope
    ) -> bool:
        result = await self.session.execute(
            select(CountryDocumentTypeModel.document_code).where(
                CountryDocumentTypeModel.country_code == country_code,
                CountryDocumentTypeModel.document_code == document_code,
                CountryDocumentTypeModel.scope == scope,
            )
        )
        return result.first() is not None
