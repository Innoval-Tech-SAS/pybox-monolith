"""Tests de `TemplateRepository` contra la base de datos real (sin mocks), mismo
patrón que `tests/receivables/test_credit_repository.py`: `db_session` corre en una
transacción por test que se revierte sola. Riesgos reales: los métodos de listado
excluyen soft-deleted (`SoftDeleteRepositoryBase`), el filtro por canal/búsqueda no
debe devolver plantillas de otro portafolio, y la paginación reporta el total real
(no el tamaño de la página).
"""

import uuid

from messaging.channels.enums.channel_enums import ChannelName
from messaging.templates.models.template_model import TemplateModel
from messaging.templates.repository.template_repository import TemplateRepository
from tests.receivables.conftest import build_organization, build_portfolio


async def _make_portfolio(db_session):
    org = build_organization()
    db_session.add(org)
    await db_session.flush()
    portfolio = build_portfolio(org.id)
    db_session.add(portfolio)
    await db_session.flush()
    return portfolio


def make_template(portfolio_id: uuid.UUID, **overrides) -> TemplateModel:
    defaults = dict(
        portfolio_id=portfolio_id,
        name=f"Plantilla {uuid.uuid4().hex[:6]}",
        channel=ChannelName.SMS,
        body="Hola {nombre}",
    )
    defaults.update(overrides)
    return TemplateModel(**defaults)


class TestListAllByPortfolioExcludesSoftDeleted:
    async def test_soft_deleted_template_is_excluded(self, db_session):
        portfolio = await _make_portfolio(db_session)
        repo = TemplateRepository(db_session)

        active = make_template(portfolio.id, name="Activa")
        deleted = make_template(portfolio.id, name="Borrada")
        db_session.add_all([active, deleted])
        await db_session.flush()
        await repo.delete(deleted)

        results = await repo.list_all_by_portfolio(portfolio.id)

        names = {t.name for t in results}
        assert "Activa" in names
        assert "Borrada" not in names


class TestListAllByPortfolioFiltersByChannel:
    async def test_only_templates_of_requested_channel_are_returned(self, db_session):
        portfolio = await _make_portfolio(db_session)
        repo = TemplateRepository(db_session)
        db_session.add_all(
            [
                make_template(portfolio.id, channel=ChannelName.SMS, body="sms"),
                make_template(
                    portfolio.id, channel=ChannelName.EMAIL, body=None, subject="asunto"
                ),
            ]
        )
        await db_session.flush()

        results = await repo.list_all_by_portfolio(
            portfolio.id, channel=ChannelName.EMAIL
        )

        assert len(results) == 1
        assert results[0].channel == ChannelName.EMAIL


class TestListByPortfolioPagination:
    async def test_total_reflects_full_count_not_page_size(self, db_session):
        portfolio = await _make_portfolio(db_session)
        repo = TemplateRepository(db_session)
        db_session.add_all(
            [make_template(portfolio.id, name=f"Plantilla {i}") for i in range(3)]
        )
        await db_session.flush()

        items, total = await repo.list_by_portfolio(portfolio.id, page=1, page_size=2)

        assert total == 3
        assert len(items) == 2

    async def test_search_filters_by_name_case_insensitive(self, db_session):
        portfolio = await _make_portfolio(db_session)
        repo = TemplateRepository(db_session)
        db_session.add_all(
            [
                make_template(portfolio.id, name="Recordatorio de pago"),
                make_template(portfolio.id, name="Bienvenida"),
            ]
        )
        await db_session.flush()

        items, total = await repo.list_by_portfolio(
            portfolio.id, page=1, page_size=10, search="recordatorio"
        )

        assert total == 1
        assert items[0].name == "Recordatorio de pago"

    async def test_templates_from_another_portfolio_are_not_included(self, db_session):
        portfolio_a = await _make_portfolio(db_session)
        portfolio_b = await _make_portfolio(db_session)
        repo = TemplateRepository(db_session)
        db_session.add_all(
            [
                make_template(portfolio_a.id, name="De A"),
                make_template(portfolio_b.id, name="De B"),
            ]
        )
        await db_session.flush()

        items, total = await repo.list_by_portfolio(
            portfolio_a.id, page=1, page_size=10
        )

        assert total == 1
        assert items[0].name == "De A"


class TestGetByIdAndPortfolio:
    async def test_returns_none_when_template_belongs_to_different_portfolio(
        self, db_session
    ):
        portfolio_a = await _make_portfolio(db_session)
        portfolio_b = await _make_portfolio(db_session)
        repo = TemplateRepository(db_session)
        template = make_template(portfolio_a.id)
        db_session.add(template)
        await db_session.flush()

        result = await repo.get_by_id_and_portfolio(template.id, portfolio_b.id)

        assert result is None

    async def test_returns_template_when_it_belongs_to_the_portfolio(self, db_session):
        portfolio = await _make_portfolio(db_session)
        repo = TemplateRepository(db_session)
        template = make_template(portfolio.id)
        db_session.add(template)
        await db_session.flush()

        result = await repo.get_by_id_and_portfolio(template.id, portfolio.id)

        assert result is not None
        assert result.id == template.id
