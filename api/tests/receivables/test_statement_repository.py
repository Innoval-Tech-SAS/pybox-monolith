"""Tests directos de `StatementRepository`: exclusión de soft-deleted, y que
`list_by_debtor` cruce organizaciones/portafolios (a diferencia de
`list_by_debtor_and_portfolio`, que sí filtra por uno)."""

import uuid
from datetime import datetime, timedelta, timezone

from app_platform.documents.models.document_model import DocumentModel
from receivables.statements.models.statement_model import StatementModel
from receivables.statements.repository.statement_repository import StatementRepository
from tests.receivables.conftest import build_credit, build_debtor, build_organization, build_portfolio


async def _fake_document(db_session) -> uuid.UUID:
    """No hace falta pasar por `DocumentService`/storage real para estos tests de
    repositorio: `document_id` solo necesita apuntar a una fila válida de `documentos`
    (FK), no a un objeto real en el almacén."""
    document = DocumentModel(
        object_key=f"test/{uuid.uuid4().hex}",
        original_name="extracto.pdf",
        content_type="application/pdf",
        size_bytes=1024,
        checksum=uuid.uuid4().hex,
    )
    db_session.add(document)
    await db_session.flush()
    return document.id


async def _setup(db_session):
    org = build_organization()
    db_session.add(org)
    await db_session.flush()
    portfolio = build_portfolio(org.id)
    db_session.add(portfolio)
    await db_session.flush()
    debtor = build_debtor(org.id)
    db_session.add(debtor)
    await db_session.flush()
    credit = build_credit(portfolio.id, debtor.id)
    db_session.add(credit)
    await db_session.flush()
    return org, portfolio, debtor, credit


def _statement(*, debtor_id, portfolio_id, organization_id, document_id, **overrides) -> StatementModel:
    defaults = dict(
        debtor_id=debtor_id,
        portfolio_id=portfolio_id,
        organization_id=organization_id,
        credit_id=None,
        cutoff_date=datetime.now(timezone.utc),
        document_id=document_id,
    )
    defaults.update(overrides)
    return StatementModel(**defaults)


class TestListByDebtorAndPortfolio:
    async def test_excludes_soft_deleted_and_other_portfolios(self, db_session):
        org, portfolio, debtor, _ = await _setup(db_session)
        other_portfolio = build_portfolio(org.id)
        db_session.add(other_portfolio)
        await db_session.flush()

        visible = _statement(
            debtor_id=debtor.id, portfolio_id=portfolio.id, organization_id=org.id,
            document_id=await _fake_document(db_session),
        )
        deleted = _statement(
            debtor_id=debtor.id, portfolio_id=portfolio.id, organization_id=org.id,
            document_id=await _fake_document(db_session), deleted_at=datetime.now(timezone.utc),
        )
        other_portfolio_statement = _statement(
            debtor_id=debtor.id, portfolio_id=other_portfolio.id, organization_id=org.id,
            document_id=await _fake_document(db_session),
        )
        db_session.add_all([visible, deleted, other_portfolio_statement])
        await db_session.flush()

        repo = StatementRepository(db_session)
        result = await repo.list_by_debtor_and_portfolio(debtor.id, portfolio.id)

        assert [s.id for s in result] == [visible.id]

    async def test_orders_most_recent_first(self, db_session):
        _, portfolio, debtor, _ = await _setup(db_session)
        now = datetime.now(timezone.utc)
        older = _statement(
            debtor_id=debtor.id, portfolio_id=portfolio.id, organization_id=portfolio.organization_id,
            document_id=await _fake_document(db_session), created_at=now - timedelta(days=1),
        )
        db_session.add(older)
        await db_session.flush()
        newer = _statement(
            debtor_id=debtor.id, portfolio_id=portfolio.id, organization_id=portfolio.organization_id,
            document_id=await _fake_document(db_session), created_at=now,
        )
        db_session.add(newer)
        await db_session.flush()

        repo = StatementRepository(db_session)
        result = await repo.list_by_debtor_and_portfolio(debtor.id, portfolio.id)

        assert [s.id for s in result] == [newer.id, older.id]


class TestListByDebtor:
    async def test_crosses_portfolios_and_organizations(self, db_session):
        org, portfolio, debtor, _ = await _setup(db_session)
        other_org = build_organization()
        db_session.add(other_org)
        await db_session.flush()
        other_portfolio = build_portfolio(other_org.id)
        db_session.add(other_portfolio)
        await db_session.flush()

        stmt_a = _statement(
            debtor_id=debtor.id, portfolio_id=portfolio.id, organization_id=org.id,
            document_id=await _fake_document(db_session),
        )
        stmt_b = _statement(
            debtor_id=debtor.id, portfolio_id=other_portfolio.id, organization_id=other_org.id,
            document_id=await _fake_document(db_session),
        )
        db_session.add_all([stmt_a, stmt_b])
        await db_session.flush()

        repo = StatementRepository(db_session)
        result = await repo.list_by_debtor([debtor.id])

        assert {s.id for s in result} == {stmt_a.id, stmt_b.id}


class TestGetOwnedByDebtorAndPortfolio:
    async def test_get_owned_by_debtor_rejects_other_debtor(self, db_session):
        org, portfolio, debtor, _ = await _setup(db_session)
        other_debtor = build_debtor(org.id)
        db_session.add(other_debtor)
        await db_session.flush()

        statement = _statement(
            debtor_id=debtor.id, portfolio_id=portfolio.id, organization_id=portfolio.organization_id,
            document_id=await _fake_document(db_session),
        )
        db_session.add(statement)
        await db_session.flush()

        repo = StatementRepository(db_session)
        assert await repo.get_owned_by_debtor(statement.id, [other_debtor.id]) is None
        assert await repo.get_owned_by_debtor(statement.id, [debtor.id]) is not None

    async def test_get_by_id_and_portfolio_rejects_other_portfolio(self, db_session):
        org, portfolio, debtor, _ = await _setup(db_session)
        other_portfolio = build_portfolio(org.id)
        db_session.add(other_portfolio)
        await db_session.flush()

        statement = _statement(
            debtor_id=debtor.id, portfolio_id=portfolio.id, organization_id=org.id,
            document_id=await _fake_document(db_session),
        )
        db_session.add(statement)
        await db_session.flush()

        repo = StatementRepository(db_session)
        assert await repo.get_by_id_and_portfolio(statement.id, other_portfolio.id) is None
        assert await repo.get_by_id_and_portfolio(statement.id, portfolio.id) is not None
