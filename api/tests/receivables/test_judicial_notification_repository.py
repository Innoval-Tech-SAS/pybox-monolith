"""Tests directos de `JudicialNotificationRepository`: inclusión del codeudor en el
buzón (no solo el titular) y exclusión de soft-deleted -- casos que
`test_judicial_notification_service.py` no ejercita porque siempre pasa por
`titular` únicamente."""

import uuid
from datetime import datetime, timezone

from receivables.judicial_notifications.enums.judicial_notification_enums import JudicialPriority
from receivables.judicial_notifications.models.judicial_notification_model import JudicialNotificationModel
from receivables.judicial_notifications.repository.judicial_notification_repository import (
    JudicialNotificationRepository,
)
from tests.receivables.conftest import build_credit, build_debtor, build_organization, build_portfolio


async def _setup_with_codebtor(db_session):
    org = build_organization()
    db_session.add(org)
    await db_session.flush()
    portfolio = build_portfolio(org.id)
    db_session.add(portfolio)
    await db_session.flush()
    titular = build_debtor(org.id)
    codebtor = build_debtor(org.id)
    db_session.add_all([titular, codebtor])
    await db_session.flush()
    credit = build_credit(portfolio.id, titular.id, codebtor_id=codebtor.id)
    db_session.add(credit)
    await db_session.flush()
    return org, portfolio, titular, codebtor, credit


class TestGetInboxByDebtorId:
    async def test_codebtor_sees_notification_in_inbox(self, db_session, real_admin_user_id):
        _, _, titular, codebtor, credit = await _setup_with_codebtor(db_session)
        notification = JudicialNotificationModel(
            credit_id=credit.id, title="T", body="B", priority=JudicialPriority.URGENT, created_by=real_admin_user_id
        )
        db_session.add(notification)
        await db_session.flush()

        repo = JudicialNotificationRepository(db_session)
        titular_inbox = await repo.get_inbox_by_debtor_ids([titular.id])
        codebtor_inbox = await repo.get_inbox_by_debtor_ids([codebtor.id])

        assert len(titular_inbox) == 1
        assert len(codebtor_inbox) == 1
        assert titular_inbox[0].notification.id == codebtor_inbox[0].notification.id

    async def test_excludes_soft_deleted(self, db_session, real_admin_user_id):
        _, _, titular, _, credit = await _setup_with_codebtor(db_session)
        active = JudicialNotificationModel(
            credit_id=credit.id, title="Activa", body="B", priority=JudicialPriority.LOW, created_by=real_admin_user_id
        )
        deleted = JudicialNotificationModel(
            credit_id=credit.id, title="Borrada", body="B", priority=JudicialPriority.LOW,
            created_by=real_admin_user_id, deleted_at=datetime.now(timezone.utc),
        )
        db_session.add_all([active, deleted])
        await db_session.flush()

        repo = JudicialNotificationRepository(db_session)
        inbox = await repo.get_inbox_by_debtor_ids([titular.id])

        assert [row.notification.id for row in inbox] == [active.id]


class TestCountUnreadByDebtorId:
    async def test_counts_only_unread_for_that_debtor(self, db_session, real_admin_user_id):
        _, _, titular, codebtor, credit = await _setup_with_codebtor(db_session)
        db_session.add_all([
            JudicialNotificationModel(
                credit_id=credit.id, title="Unread", body="B", priority=JudicialPriority.LOW,
                created_by=real_admin_user_id, is_read=False,
            ),
            JudicialNotificationModel(
                credit_id=credit.id, title="Read", body="B", priority=JudicialPriority.LOW,
                created_by=real_admin_user_id, is_read=True,
            ),
        ])
        await db_session.flush()

        repo = JudicialNotificationRepository(db_session)
        assert await repo.count_unread_by_debtor_ids([titular.id]) == 1
        assert await repo.count_unread_by_debtor_ids([codebtor.id]) == 1


class TestMarkAllReadByDebtorId:
    async def test_only_marks_notifications_of_that_debtors_credits(self, db_session, real_admin_user_id):
        org, portfolio, titular, codebtor, credit = await _setup_with_codebtor(db_session)
        other_debtor = build_debtor(org.id)
        db_session.add(other_debtor)
        await db_session.flush()
        other_credit = build_credit(portfolio.id, other_debtor.id)
        db_session.add(other_credit)
        await db_session.flush()

        mine = JudicialNotificationModel(
            credit_id=credit.id, title="Mine", body="B", priority=JudicialPriority.LOW,
            created_by=real_admin_user_id, is_read=False,
        )
        others = JudicialNotificationModel(
            credit_id=other_credit.id, title="Others", body="B", priority=JudicialPriority.LOW,
            created_by=real_admin_user_id, is_read=False,
        )
        db_session.add_all([mine, others])
        await db_session.flush()

        repo = JudicialNotificationRepository(db_session)
        await repo.mark_all_read_by_debtor_ids([titular.id])

        await db_session.refresh(mine)
        await db_session.refresh(others)
        assert mine.is_read is True
        assert others.is_read is False


class TestGetCreditRecipients:
    async def test_returns_titular_and_codebtor(self, db_session):
        _, _, titular, codebtor, credit = await _setup_with_codebtor(db_session)

        repo = JudicialNotificationRepository(db_session)
        recipients = await repo.get_credit_recipients(credit.id)

        assert {d.id for d in recipients} == {titular.id, codebtor.id}

    async def test_credit_without_codebtor_returns_only_titular(self, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        titular = build_debtor(org.id)
        db_session.add(titular)
        await db_session.flush()
        credit = build_credit(portfolio.id, titular.id)
        db_session.add(credit)
        await db_session.flush()

        repo = JudicialNotificationRepository(db_session)
        recipients = await repo.get_credit_recipients(credit.id)

        assert {d.id for d in recipients} == {titular.id}


class TestGetCreditOrganizationId:
    async def test_returns_none_for_unknown_credit(self, db_session):
        repo = JudicialNotificationRepository(db_session)
        assert await repo.get_credit_organization_id(uuid.uuid4()) is None

    async def test_returns_none_for_soft_deleted_credit(self, db_session):
        org, portfolio, titular, _, credit = await _setup_with_codebtor(db_session)
        credit.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()

        repo = JudicialNotificationRepository(db_session)
        assert await repo.get_credit_organization_id(credit.id) is None
