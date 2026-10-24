"""Tests de integración de WhatsAppTemplateDataRepository (ver whatsapp_template_data_repository.py)."""

from messaging.whatsapp.repository.whatsapp_template_data_repository import (
    WhatsAppTemplateDataRepository,
)
from tests.messaging.whatsapp.conftest import build_template, build_template_data


class TestGetByTemplateId:
    async def test_finds_the_1to1_row(self, db_session, real_portfolio):
        template = build_template(real_portfolio.id)
        db_session.add(template)
        await db_session.flush()
        data = build_template_data(template.id)
        db_session.add(data)
        await db_session.flush()
        repo = WhatsAppTemplateDataRepository(db_session)

        result = await repo.get_by_template_id(template.id)

        assert result is not None
        assert result.id == data.id

    async def test_template_without_data_row_returns_none(
        self, db_session, real_portfolio
    ):
        template = build_template(real_portfolio.id)
        db_session.add(template)
        await db_session.flush()
        repo = WhatsAppTemplateDataRepository(db_session)

        assert await repo.get_by_template_id(template.id) is None

    async def test_soft_deleted_row_is_not_returned(self, db_session, real_portfolio):
        template = build_template(real_portfolio.id)
        db_session.add(template)
        await db_session.flush()
        data = build_template_data(template.id)
        db_session.add(data)
        await db_session.flush()
        repo = WhatsAppTemplateDataRepository(db_session)
        await repo.delete(data)

        assert await repo.get_by_template_id(template.id) is None


class TestGetByTemplateIds:
    async def test_empty_list_returns_empty_without_querying(self, db_session):
        repo = WhatsAppTemplateDataRepository(db_session)
        assert await repo.get_by_template_ids([]) == []

    async def test_returns_only_rows_for_requested_templates(
        self, db_session, real_portfolio
    ):
        template_a = build_template(real_portfolio.id)
        template_b = build_template(real_portfolio.id)
        template_c = build_template(real_portfolio.id)
        db_session.add_all([template_a, template_b, template_c])
        await db_session.flush()
        data_a = build_template_data(template_a.id)
        data_b = build_template_data(template_b.id)
        data_c = build_template_data(template_c.id)
        db_session.add_all([data_a, data_b, data_c])
        await db_session.flush()
        repo = WhatsAppTemplateDataRepository(db_session)

        result = await repo.get_by_template_ids([template_a.id, template_b.id])

        assert {row.id for row in result} == {data_a.id, data_b.id}
