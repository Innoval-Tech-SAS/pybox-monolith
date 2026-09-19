"""Tests directos de `SegmentRepository`/`SegmentExecutionRepository` contra la base
real: exclusión de soft-deleted y orden de resultados, que `test_segment_service.py`
no cubre porque pasa siempre por segmentos recién creados."""

import uuid
from datetime import datetime, timedelta, timezone

from receivables.segments.models.segment_execution_model import SegmentExecutionModel
from receivables.segments.models.segment_model import SegmentModel
from receivables.segments.repository.segment_execution_repository import SegmentExecutionRepository
from receivables.segments.repository.segment_repository import SegmentRepository
from tests.receivables.conftest import build_organization, build_portfolio


async def _org_and_portfolio(db_session):
    org = build_organization()
    db_session.add(org)
    await db_session.flush()
    portfolio = build_portfolio(org.id)
    db_session.add(portfolio)
    await db_session.flush()
    return org, portfolio


class TestGetAllByPortfolio:
    async def test_excludes_soft_deleted(self, db_session):
        _, portfolio = await _org_and_portfolio(db_session)
        active = SegmentModel(name="Activo", filter_criteria={"tables": []}, portfolio_id=portfolio.id)
        deleted = SegmentModel(
            name="Borrado",
            filter_criteria={"tables": []},
            portfolio_id=portfolio.id,
            deleted_at=datetime.now(timezone.utc),
        )
        db_session.add_all([active, deleted])
        await db_session.flush()

        repo = SegmentRepository(db_session)
        result = await repo.get_all_by_portfolio(portfolio.id)

        assert [s.id for s in result] == [active.id]


class TestGetByPortfolio:
    async def test_total_excludes_soft_deleted_and_other_portfolios(self, db_session):
        org, portfolio = await _org_and_portfolio(db_session)
        other_portfolio = build_portfolio(org.id)
        db_session.add(other_portfolio)
        await db_session.flush()

        db_session.add_all([
            SegmentModel(name="A", filter_criteria={"tables": []}, portfolio_id=portfolio.id),
            SegmentModel(name="B", filter_criteria={"tables": []}, portfolio_id=portfolio.id),
            SegmentModel(
                name="Borrado",
                filter_criteria={"tables": []},
                portfolio_id=portfolio.id,
                deleted_at=datetime.now(timezone.utc),
            ),
            SegmentModel(name="Otro portafolio", filter_criteria={"tables": []}, portfolio_id=other_portfolio.id),
        ])
        await db_session.flush()

        repo = SegmentRepository(db_session)
        items, total = await repo.get_by_portfolio(portfolio.id, page=1, page_size=10)

        assert total == 2
        assert len(items) == 2

    async def test_pagination_second_page(self, db_session):
        _, portfolio = await _org_and_portfolio(db_session)
        for i in range(3):
            db_session.add(SegmentModel(name=f"Seg {i}", filter_criteria={"tables": []}, portfolio_id=portfolio.id))
        await db_session.flush()

        repo = SegmentRepository(db_session)
        items, total = await repo.get_by_portfolio(portfolio.id, page=2, page_size=2)

        assert total == 3
        assert len(items) == 1


class TestGetByIdAndPortfolio:
    async def test_none_when_portfolio_does_not_match(self, db_session):
        org, portfolio = await _org_and_portfolio(db_session)
        other_portfolio = build_portfolio(org.id)
        db_session.add(other_portfolio)
        await db_session.flush()
        segment = SegmentModel(name="Seg", filter_criteria={"tables": []}, portfolio_id=portfolio.id)
        db_session.add(segment)
        await db_session.flush()

        repo = SegmentRepository(db_session)
        result = await repo.get_by_id_and_portfolio(segment.id, other_portfolio.id)

        assert result is None


class TestSegmentExecutionRepository:
    async def test_get_by_segment_orders_most_recent_first(self, db_session, real_admin_user_id):
        _, portfolio = await _org_and_portfolio(db_session)
        segment = SegmentModel(name="Seg", filter_criteria={"tables": []}, portfolio_id=portfolio.id)
        db_session.add(segment)
        await db_session.flush()

        now = datetime.now(timezone.utc)
        older = SegmentExecutionModel(
            segment_id=segment.id, mode="preview", rows=1, columns=["a"], executed_by=real_admin_user_id,
            created_at=now - timedelta(days=1),
        )
        db_session.add(older)
        await db_session.flush()
        newer = SegmentExecutionModel(
            segment_id=segment.id, mode="audit", rows=2, columns=["a"], executed_by=real_admin_user_id,
            created_at=now,
        )
        db_session.add(newer)
        await db_session.flush()

        repo = SegmentExecutionRepository(db_session)
        result = await repo.get_by_segment(segment.id)

        assert [e.id for e in result] == [newer.id, older.id]

    async def test_get_by_segment_excludes_other_segments(self, db_session, real_admin_user_id):
        _, portfolio = await _org_and_portfolio(db_session)
        segment_a = SegmentModel(name="A", filter_criteria={"tables": []}, portfolio_id=portfolio.id)
        segment_b = SegmentModel(name="B", filter_criteria={"tables": []}, portfolio_id=portfolio.id)
        db_session.add_all([segment_a, segment_b])
        await db_session.flush()

        exec_a = SegmentExecutionModel(
            segment_id=segment_a.id, mode="preview", rows=1, columns=["a"], executed_by=real_admin_user_id
        )
        exec_b = SegmentExecutionModel(
            segment_id=segment_b.id, mode="preview", rows=1, columns=["a"], executed_by=real_admin_user_id
        )
        db_session.add_all([exec_a, exec_b])
        await db_session.flush()

        repo = SegmentExecutionRepository(db_session)
        result = await repo.get_by_segment(segment_a.id)

        assert [e.id for e in result] == [exec_a.id]
