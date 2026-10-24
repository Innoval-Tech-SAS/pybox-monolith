"""Tests de integración de WhatsAppSendErrorRepository (ver whatsapp_send_error_repository.py).

`list_by_organization` solo puede resolver la organización dueña de un error a
través de un JOIN con `contactos` -- un error sin `contact_id` matcheado nunca
aparece en el listado por organización, aunque exista en la tabla.
"""

from messaging.contacts.models.contact_model import ContactModel
from messaging.whatsapp.repository.whatsapp_send_error_repository import (
    WhatsAppSendErrorRepository,
)
from tests.messaging.whatsapp.conftest import build_send_error


def build_contact(organization_id, **overrides) -> ContactModel:
    defaults = dict(
        content="mensaje", recipient="573000000000", organization_id=organization_id
    )
    defaults.update(overrides)
    return ContactModel(**defaults)


class TestGetByWamid:
    async def test_finds_by_wamid(self, db_session):
        error = build_send_error(wamid="wamid.err-1")
        db_session.add(error)
        await db_session.flush()
        repo = WhatsAppSendErrorRepository(db_session)

        result = await repo.get_by_wamid("wamid.err-1")

        assert result is not None
        assert result.id == error.id

    async def test_unknown_wamid_returns_none(self, db_session):
        repo = WhatsAppSendErrorRepository(db_session)
        assert await repo.get_by_wamid("wamid.no-existe") is None


class TestGetByWamidAndCode:
    async def test_matches_only_same_wamid_and_code(self, db_session):
        db_session.add(build_send_error(wamid="wamid.1", error_code=131047))
        await db_session.flush()
        repo = WhatsAppSendErrorRepository(db_session)

        assert await repo.get_by_wamid_and_code("wamid.1", 131047) is not None
        assert await repo.get_by_wamid_and_code("wamid.1", 999) is None


class TestListByOrganization:
    async def test_lists_only_errors_whose_contact_belongs_to_the_organization(
        self, db_session, real_org
    ):
        from tests.messaging.whatsapp.conftest import build_organization

        other_org = build_organization()
        db_session.add(other_org)
        await db_session.flush()

        contact_mine = build_contact(real_org.id)
        contact_other = build_contact(other_org.id)
        db_session.add_all([contact_mine, contact_other])
        await db_session.flush()

        error_mine = build_send_error(contact_id=contact_mine.id)
        error_other = build_send_error(contact_id=contact_other.id)
        error_orphan = build_send_error(contact_id=None)  # sin contacto matcheado
        db_session.add_all([error_mine, error_other, error_orphan])
        await db_session.flush()

        repo = WhatsAppSendErrorRepository(db_session)
        items, total = await repo.list_by_organization(real_org.id, 1, 20)

        assert total == 1
        assert items[0].id == error_mine.id

    async def test_soft_deleted_errors_are_excluded(self, db_session, real_org):
        contact = build_contact(real_org.id)
        db_session.add(contact)
        await db_session.flush()
        error = build_send_error(contact_id=contact.id)
        db_session.add(error)
        await db_session.flush()
        repo = WhatsAppSendErrorRepository(db_session)
        await repo.delete(error)

        _items, total = await repo.list_by_organization(real_org.id, 1, 20)

        assert total == 0

    async def test_orders_most_recent_first(self, db_session, real_org):
        from datetime import datetime, timedelta, timezone

        contact = build_contact(real_org.id)
        db_session.add(contact)
        await db_session.flush()
        now = datetime.now(timezone.utc)
        older = build_send_error(
            contact_id=contact.id, occurred_at=now - timedelta(days=1)
        )
        newer = build_send_error(contact_id=contact.id, occurred_at=now)
        db_session.add_all([older, newer])
        await db_session.flush()
        repo = WhatsAppSendErrorRepository(db_session)

        items, _total = await repo.list_by_organization(real_org.id, 1, 20)

        assert [item.id for item in items] == [newer.id, older.id]
