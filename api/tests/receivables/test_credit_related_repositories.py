"""Queries reales de los repositorios auxiliares de crédito: `UVRQuoteRepository`,
`CreditAdjustmentRepository` y `CreditSettlementTicketRepository` -- contra
`db_session`, sin mocks.
"""

from datetime import datetime, timezone

from app_platform.support.enums.support_enums import SupportCaseType, SupportTicketStatus
from app_platform.support.models.support_ticket_model import SupportTicketModel
from receivables.credits.models.credit_adjustment_model import CreditAdjustmentModel
from receivables.credits.models.credit_settlement_ticket_model import CreditSettlementTicketModel
from receivables.credits.models.uvr_quote_model import UVRQuoteModel
from receivables.credits.repository.credit_adjustment_repository import CreditAdjustmentRepository
from receivables.credits.repository.credit_settlement_ticket_repository import CreditSettlementTicketRepository
from receivables.credits.repository.uvr_quote_repository import UVRQuoteRepository
from tests.receivables.conftest import build_credit, build_debtor, build_organization, build_portfolio


class TestUVRQuoteRepository:
    async def test_get_by_credit_id_returns_only_that_credit_quotes(self, db_session, real_credit):
        other_org = build_organization()
        db_session.add(other_org)
        await db_session.flush()
        other_portfolio = build_portfolio(other_org.id)
        db_session.add(other_portfolio)
        await db_session.flush()
        other_debtor = build_debtor()
        db_session.add(other_debtor)
        await db_session.flush()
        other_credit = build_credit(other_portfolio.id, other_debtor.id)
        db_session.add(other_credit)
        await db_session.flush()

        mine = UVRQuoteModel(credit_id=real_credit.id, quote_value=350.5, quote_date=datetime.now(timezone.utc))
        other = UVRQuoteModel(credit_id=other_credit.id, quote_value=999, quote_date=datetime.now(timezone.utc))
        db_session.add_all([mine, other])
        await db_session.flush()

        repo = UVRQuoteRepository(db_session)
        result = await repo.get_by_credit_id(real_credit.id)

        assert {q.id for q in result} == {mine.id}

    async def test_get_by_date_finds_the_exact_match(self, db_session, real_credit):
        quote_date = datetime(2026, 1, 5, tzinfo=timezone.utc)
        quote = UVRQuoteModel(credit_id=real_credit.id, quote_value=350.5, quote_date=quote_date)
        db_session.add(quote)
        await db_session.flush()

        repo = UVRQuoteRepository(db_session)
        found = await repo.get_by_date(quote_date)

        assert found is not None
        assert found.id == quote.id

    async def test_get_by_date_returns_none_when_no_match(self, db_session):
        repo = UVRQuoteRepository(db_session)
        assert await repo.get_by_date(datetime(1999, 1, 1, tzinfo=timezone.utc)) is None


class TestCreditAdjustmentRepository:
    async def test_get_by_credit_id_returns_only_that_credit_adjustments(self, db_session, real_credit):
        other_org = build_organization()
        db_session.add(other_org)
        await db_session.flush()
        other_portfolio = build_portfolio(other_org.id)
        db_session.add(other_portfolio)
        await db_session.flush()
        other_debtor = build_debtor()
        db_session.add(other_debtor)
        await db_session.flush()
        other_credit = build_credit(other_portfolio.id, other_debtor.id)
        db_session.add(other_credit)
        await db_session.flush()

        mine = CreditAdjustmentModel(
            credit_id=real_credit.id, adjustment_type="CONDONACION", adjustment_amount=5000,
            applied_date=datetime.now(timezone.utc),
        )
        other = CreditAdjustmentModel(
            credit_id=other_credit.id, adjustment_type="CONDONACION", adjustment_amount=1000,
            applied_date=datetime.now(timezone.utc),
        )
        db_session.add_all([mine, other])
        await db_session.flush()

        repo = CreditAdjustmentRepository(db_session)
        result = await repo.get_by_credit_id(real_credit.id)

        assert {a.id for a in result} == {mine.id}

    async def test_get_by_credit_id_empty_when_none_exist(self, db_session, real_credit):
        repo = CreditAdjustmentRepository(db_session)
        assert await repo.get_by_credit_id(real_credit.id) == []


async def _create_ticket(db_session, credit, real_admin_user_id, status=SupportTicketStatus.OPEN):
    ticket = SupportTicketModel(
        case_type=SupportCaseType.REQUIREMENT,
        status=status,
        organization_id=None,
        created_by=real_admin_user_id,
    )
    db_session.add(ticket)
    await db_session.flush()
    link = CreditSettlementTicketModel(ticket_id=ticket.id, credit_id=credit.id, settlement_amount=1000)
    db_session.add(link)
    await db_session.flush()
    return ticket, link


class TestCreditSettlementTicketRepository:
    async def test_get_by_ticket_id_returns_the_link(self, db_session, real_credit, real_admin_user_id):
        ticket, link = await _create_ticket(db_session, real_credit, real_admin_user_id)

        repo = CreditSettlementTicketRepository(db_session)
        found = await repo.get_by_ticket_id(ticket.id)

        assert found is not None
        assert found.id == link.id

    async def test_get_active_by_credit_id_finds_open_ticket(self, db_session, real_credit, real_admin_user_id):
        await _create_ticket(db_session, real_credit, real_admin_user_id, status=SupportTicketStatus.OPEN)

        repo = CreditSettlementTicketRepository(db_session)
        found = await repo.get_active_by_credit_id(real_credit.id)

        assert found is not None

    async def test_get_active_by_credit_id_ignores_resolved_ticket(self, db_session, real_credit, real_admin_user_id):
        await _create_ticket(db_session, real_credit, real_admin_user_id, status=SupportTicketStatus.RESOLVED)

        repo = CreditSettlementTicketRepository(db_session)
        found = await repo.get_active_by_credit_id(real_credit.id)

        assert found is None

    async def test_get_active_by_credit_id_ignores_closed_ticket(self, db_session, real_credit, real_admin_user_id):
        await _create_ticket(db_session, real_credit, real_admin_user_id, status=SupportTicketStatus.CLOSED)

        repo = CreditSettlementTicketRepository(db_session)
        found = await repo.get_active_by_credit_id(real_credit.id)

        assert found is None

    async def test_get_active_by_credit_id_none_when_no_ticket(self, db_session, real_credit):
        repo = CreditSettlementTicketRepository(db_session)
        assert await repo.get_active_by_credit_id(real_credit.id) is None
