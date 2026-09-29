from app_platform.countries.enums.country_enums import DocumentScope
from app_platform.countries.repository.country_repository import CountryRepository
from app_platform.countries.schemas.countries_schemas import (
    DocumentTypeGroup,
    DocumentTypeOption,
    DocumentTypesResponse,
    NationalityOption,
)


def _flag_emoji(country_code: str) -> str:
    """Emoji de bandera (regional indicators) a partir del código ISO de 2 letras."""
    if len(country_code) != 2 or not country_code.isalpha():
        return "🌍"
    return "".join(chr(0x1F1E6 + ord(char) - ord("A")) for char in country_code.upper())


class CountryService:
    def __init__(self, repository: CountryRepository):
        self.repository = repository

    async def list_countries(self) -> list[NationalityOption]:
        countries = await self.repository.list_active()
        person_docs = await self.repository.list_document_map(DocumentScope.PERSON)
        fiscal_docs = await self.repository.list_document_map(DocumentScope.ORG_FISCAL)
        mercantile_docs = await self.repository.list_document_map(
            DocumentScope.ORG_MERCANTILE
        )
        return [
            NationalityOption(
                code=country.code,
                name=country.name,
                flag_url=country.flag_url,
                phone_prefix=country.phone_prefix,
                timezone=country.timezone,
                currency_code=country.currency_code,
                document_types=person_docs.get(country.code, []),
                fiscal_document_types=fiscal_docs.get(country.code, []),
                mercantile_document_types=mercantile_docs.get(country.code, []),
            )
            for country in countries
        ]

    async def get_document_types(self) -> DocumentTypesResponse:
        """Labels (código→etiqueta) + grupos de documentos de persona por país,
        para que el frontend deje de depender de su dict estático. Los códigos
        comunes a TODOS los países (p. ej. PASAPORTE) se agrupan en 'Universal'."""
        countries = await self.repository.list_active()
        person_map = await self.repository.list_document_map(DocumentScope.PERSON)
        labels = await self.repository.get_document_labels()

        country_codes = [country.code for country in countries]
        all_person_codes = {code for codes in person_map.values() for code in codes}
        universal = {
            code
            for code in all_person_codes
            if country_codes
            and all(code in person_map.get(cc, []) for cc in country_codes)
        }

        groups: list[DocumentTypeGroup] = []
        for country in countries:
            options = [
                DocumentTypeOption(
                    value=code, label=f"{code} – {labels.get(code, code)}"
                )
                for code in person_map.get(country.code, [])
                if code not in universal
            ]
            if options:
                groups.append(
                    DocumentTypeGroup(
                        group=f"{_flag_emoji(country.code)} {country.name}",
                        options=options,
                    )
                )
        if universal:
            groups.append(
                DocumentTypeGroup(
                    group="🌎 Universal",
                    options=[
                        DocumentTypeOption(value=code, label=labels.get(code, code))
                        for code in sorted(universal)
                    ],
                )
            )

        return DocumentTypesResponse(labels=labels, groups=groups)

    async def is_document_valid_for_country(
        self, country_code: str, document_code: str, scope: DocumentScope
    ) -> bool:
        return await self.repository.is_document_valid_for_country(
            country_code, document_code, scope
        )

    async def require_valid_country(
        self, code: str | None, *, required: bool = True
    ) -> str | None:
        """Valida contra DB que el código sea un país activo. Devuelve el código o lanza
        ValueError. Reemplaza la validación contra el StrEnum estático `Nationality`."""
        if not code:
            if required:
                raise ValueError("El país es obligatorio.")
            return None
        country = await self.repository.get_by_code(code)
        if country is None or not country.is_active:
            raise ValueError(f"El país '{code}' no es válido.")
        return country.code

    async def require_valid_document(
        self,
        document_code: str | None,
        scope: DocumentScope,
        country_code: str | None = None,
        *,
        required: bool = False,
    ) -> str | None:
        """Valida contra DB un código de documento. Si se da `country_code`,
        exige que el documento aplique a ese país en el alcance dado
        (`paises_tipos_documento`); si no, solo exige que el código exista en el
        catálogo `tipos_documento`. Reemplaza la validación contra
        `DOCUMENTS_BY_NATIONALITY` / `UserDocumentType`."""
        if not document_code:
            if required:
                raise ValueError("El tipo de documento es obligatorio.")
            return None
        if country_code:
            valid = await self.repository.is_document_valid_for_country(
                country_code, document_code, scope
            )
            if not valid:
                raise ValueError(
                    f"El tipo de documento '{document_code}' no es válido para "
                    f"el país '{country_code}'."
                )
        else:
            labels = await self.repository.get_document_labels()
            if document_code not in labels:
                raise ValueError(
                    f"El tipo de documento '{document_code}' no es válido."
                )
        return document_code
