"""Tests de `CountryRepository`/`CountryService` contra DB real (países sembrados por
`seed_countries` en `conftest.py`). Cierra las ramas de fallback (país/documento
desconocido) y de validación cruzada país+documento que no pasan por HTTP."""

import pytest

from app_platform.countries.enums.country_enums import DocumentScope
from app_platform.countries.repository.country_repository import CountryRepository
from app_platform.countries.services.country_service import CountryService


@pytest.fixture
def repo(db_session) -> CountryRepository:
    return CountryRepository(db_session)


@pytest.fixture
def service(repo: CountryRepository) -> CountryService:
    return CountryService(repo)


class TestRepositoryDefaults:
    async def test_get_currency_code_known_country(self, repo: CountryRepository):
        assert await repo.get_currency_code("CO") == "COP"

    async def test_get_currency_code_unknown_country_falls_back_to_default(self, repo: CountryRepository):
        assert await repo.get_currency_code("ZZ") == "COP"

    async def test_get_currency_code_none_falls_back_to_default(self, repo: CountryRepository):
        assert await repo.get_currency_code(None) == "COP"

    async def test_get_currency_code_custom_default(self, repo: CountryRepository):
        assert await repo.get_currency_code("ZZ", default="USD") == "USD"

    async def test_get_timezone_known_country(self, repo: CountryRepository):
        tz = await repo.get_timezone("CO")
        assert tz and tz != "UTC"

    async def test_get_timezone_unknown_falls_back_to_utc(self, repo: CountryRepository):
        assert await repo.get_timezone("ZZ") == "UTC"

    async def test_get_phone_prefix_known_country(self, repo: CountryRepository):
        assert await repo.get_phone_prefix("CO") == "+57"

    async def test_get_phone_prefix_unknown_country_returns_none(self, repo: CountryRepository):
        assert await repo.get_phone_prefix("ZZ") is None

    async def test_get_phone_prefix_none_code_returns_none(self, repo: CountryRepository):
        assert await repo.get_phone_prefix(None) is None

    async def test_get_active_map_contains_seeded_countries(self, repo: CountryRepository):
        mapping = await repo.get_active_map()
        assert "CO" in mapping
        assert mapping["CO"].code == "CO"


class TestDocumentValidation:
    async def test_is_document_valid_for_country_true_for_cc_in_colombia(self, repo: CountryRepository):
        assert await repo.is_document_valid_for_country("CO", "CC", DocumentScope.PERSON) is True

    async def test_is_document_valid_for_country_false_for_unknown_code(self, repo: CountryRepository):
        assert await repo.is_document_valid_for_country("CO", "NO_EXISTE", DocumentScope.PERSON) is False

    async def test_get_document_code_returns_first_match(self, repo: CountryRepository):
        code = await repo.get_document_code("CO", DocumentScope.ORG_FISCAL)
        assert code is not None

    async def test_get_document_code_unknown_country_returns_none(self, repo: CountryRepository):
        assert await repo.get_document_code("ZZ", DocumentScope.ORG_FISCAL) is None


class TestServiceRequireValidCountry:
    async def test_valid_active_country_returns_code(self, service: CountryService):
        assert await service.require_valid_country("CO") == "CO"

    async def test_unknown_country_raises_value_error(self, service: CountryService):
        with pytest.raises(ValueError, match="no es válido"):
            await service.require_valid_country("ZZ")

    async def test_missing_required_country_raises(self, service: CountryService):
        with pytest.raises(ValueError, match="obligatorio"):
            await service.require_valid_country(None)

    async def test_missing_optional_country_returns_none(self, service: CountryService):
        assert await service.require_valid_country(None, required=False) is None


class TestServiceRequireValidDocument:
    async def test_valid_document_for_country(self, service: CountryService):
        result = await service.require_valid_document("CC", DocumentScope.PERSON, country_code="CO")
        assert result == "CC"

    async def test_invalid_document_for_country_raises(self, service: CountryService):
        with pytest.raises(ValueError, match="no es válido para el país"):
            await service.require_valid_document("NO_EXISTE", DocumentScope.PERSON, country_code="CO")

    async def test_valid_document_without_country_checks_global_catalog(self, service: CountryService):
        result = await service.require_valid_document("CC", DocumentScope.PERSON)
        assert result == "CC"

    async def test_unknown_document_without_country_raises(self, service: CountryService):
        with pytest.raises(ValueError, match="no es válido"):
            await service.require_valid_document("NO_EXISTE", DocumentScope.PERSON)

    async def test_missing_optional_document_returns_none(self, service: CountryService):
        assert await service.require_valid_document(None, DocumentScope.PERSON) is None

    async def test_missing_required_document_raises(self, service: CountryService):
        with pytest.raises(ValueError, match="obligatorio"):
            await service.require_valid_document(None, DocumentScope.PERSON, required=True)
