"""Tests de integración de WhatsAppOrgCredentialsRepository (ver whatsapp_org_credentials_repository.py)."""

from messaging.whatsapp.repository.whatsapp_org_credentials_repository import (
    WhatsAppOrgCredentialsRepository,
)
from tests.messaging.whatsapp.conftest import build_credentials


class TestGetByOrganization:
    async def test_finds_the_row(self, db_session, real_org):
        credentials = build_credentials(real_org.id)
        db_session.add(credentials)
        await db_session.flush()
        repo = WhatsAppOrgCredentialsRepository(db_session)

        result = await repo.get_by_organization(real_org.id)

        assert result is not None
        assert result.id == credentials.id

    async def test_org_without_credentials_returns_none(self, db_session, real_org):
        repo = WhatsAppOrgCredentialsRepository(db_session)
        assert await repo.get_by_organization(real_org.id) is None

    async def test_soft_deleted_row_is_not_returned(self, db_session, real_org):
        credentials = build_credentials(real_org.id)
        db_session.add(credentials)
        await db_session.flush()
        repo = WhatsAppOrgCredentialsRepository(db_session)
        await repo.delete(credentials)

        assert await repo.get_by_organization(real_org.id) is None


class TestGetByPhoneNumberId:
    async def test_finds_the_row(self, db_session, real_org):
        credentials = build_credentials(real_org.id, phone_number_id="phone-abc-123")
        db_session.add(credentials)
        await db_session.flush()
        repo = WhatsAppOrgCredentialsRepository(db_session)

        result = await repo.get_by_phone_number_id("phone-abc-123")

        assert result is not None
        assert result.organization_id == real_org.id

    async def test_unknown_phone_number_id_returns_none(self, db_session):
        repo = WhatsAppOrgCredentialsRepository(db_session)
        assert await repo.get_by_phone_number_id("no-existe") is None
