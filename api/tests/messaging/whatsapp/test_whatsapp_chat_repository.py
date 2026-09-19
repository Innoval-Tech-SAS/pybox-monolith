"""Tests de integración de WhatsAppChatRepository contra la base de datos real
(ver whatsapp_chat_repository.py) -- transacción por test, revertida al final
(ver `db_session` en tests/conftest.py).
"""

import uuid

from messaging.whatsapp.repository.whatsapp_chat_repository import OrgChatScope, WhatsAppChatRepository
from tests.messaging.whatsapp.conftest import build_chat


class TestGetByOrgAndPhone:
    async def test_finds_existing_chat(self, db_session, real_org):
        chat = build_chat(real_org.id, phone="573001112233")
        db_session.add(chat)
        await db_session.flush()
        repo = WhatsAppChatRepository(db_session)

        result = await repo.get_by_org_and_phone(real_org.id, "573001112233")

        assert result is not None
        assert result.id == chat.id

    async def test_different_phone_returns_none(self, db_session, real_org):
        db_session.add(build_chat(real_org.id, phone="573001112233"))
        await db_session.flush()
        repo = WhatsAppChatRepository(db_session)

        result = await repo.get_by_org_and_phone(real_org.id, "573009998877")

        assert result is None

    async def test_soft_deleted_chat_is_not_returned(self, db_session, real_org):
        chat = build_chat(real_org.id, phone="573001112233")
        db_session.add(chat)
        await db_session.flush()
        repo = WhatsAppChatRepository(db_session)
        await repo.delete(chat)

        result = await repo.get_by_org_and_phone(real_org.id, "573001112233")

        assert result is None


class TestListByScopes:
    async def test_unrestricted_ignores_scopes_and_returns_all(self, db_session, real_org):
        db_session.add(build_chat(real_org.id))
        db_session.add(build_chat(real_org.id))
        await db_session.flush()
        repo = WhatsAppChatRepository(db_session)

        items, total = await repo.list_by_scopes([], 1, 20, unrestricted=True)

        assert total == 2
        assert len(items) == 2

    async def test_no_scopes_and_not_unrestricted_returns_empty(self, db_session, real_org):
        db_session.add(build_chat(real_org.id))
        await db_session.flush()
        repo = WhatsAppChatRepository(db_session)

        items, total = await repo.list_by_scopes([], 1, 20, unrestricted=False)

        assert (items, total) == ([], 0)

    async def test_scope_with_assigned_user_filters_to_that_user_only(self, db_session, real_org, make_real_user_id):
        agent_id = await make_real_user_id()
        other_agent_id = await make_real_user_id()
        mine = build_chat(real_org.id, assigned_user_id=agent_id)
        others = build_chat(real_org.id, assigned_user_id=other_agent_id)
        db_session.add_all([mine, others])
        await db_session.flush()
        repo = WhatsAppChatRepository(db_session)

        items, total = await repo.list_by_scopes(
            [OrgChatScope(organization_id=real_org.id, assigned_user_id=agent_id)], 1, 20
        )

        assert total == 1
        assert items[0].id == mine.id

    async def test_scope_with_portfolio_ids_excludes_chats_without_portfolio(
        self, db_session, real_org, real_portfolio
    ):
        with_portfolio = build_chat(real_org.id, portfolio_id=real_portfolio.id)
        without_portfolio = build_chat(real_org.id, portfolio_id=None)
        db_session.add_all([with_portfolio, without_portfolio])
        await db_session.flush()
        repo = WhatsAppChatRepository(db_session)

        items, total = await repo.list_by_scopes(
            [OrgChatScope(organization_id=real_org.id, portfolio_ids=[real_portfolio.id])], 1, 20
        )

        assert total == 1
        assert items[0].id == with_portfolio.id

    async def test_scope_with_none_portfolio_ids_means_unrestricted_within_org(self, db_session, real_org):
        """`portfolio_ids=None` (admin de la org) no filtra -- a diferencia de una
        lista vacía, que excluiría todo."""
        chat = build_chat(real_org.id, portfolio_id=None)
        db_session.add(chat)
        await db_session.flush()
        repo = WhatsAppChatRepository(db_session)

        items, total = await repo.list_by_scopes([OrgChatScope(organization_id=real_org.id)], 1, 20)

        assert total == 1

    async def test_multiple_org_scopes_are_ored_together(self, db_session, real_org):
        from tests.messaging.whatsapp.conftest import build_organization

        other_org = build_organization()
        db_session.add(other_org)
        await db_session.flush()
        db_session.add(build_chat(real_org.id))
        db_session.add(build_chat(other_org.id))
        await db_session.flush()
        repo = WhatsAppChatRepository(db_session)

        items, total = await repo.list_by_scopes(
            [OrgChatScope(organization_id=real_org.id), OrgChatScope(organization_id=other_org.id)], 1, 20
        )

        assert total == 2

    async def test_pagination_limits_and_offsets_results(self, db_session, real_org):
        for _ in range(3):
            db_session.add(build_chat(real_org.id))
        await db_session.flush()
        repo = WhatsAppChatRepository(db_session)

        page1, total = await repo.list_by_scopes([], 1, 2, unrestricted=True)
        page2, _total = await repo.list_by_scopes([], 2, 2, unrestricted=True)

        assert total == 3
        assert len(page1) == 2
        assert len(page2) == 1


class TestGetLeastLoadedUser:
    async def test_no_candidates_returns_none(self, db_session):
        repo = WhatsAppChatRepository(db_session)

        assert await repo.get_least_loaded_user([]) is None

    async def test_candidate_without_any_chat_has_zero_load(self, db_session, real_org, make_real_user_id):
        busy_agent = await make_real_user_id()
        idle_agent = await make_real_user_id()
        db_session.add(build_chat(real_org.id, assigned_user_id=busy_agent))
        db_session.add(build_chat(real_org.id, assigned_user_id=busy_agent))
        await db_session.flush()
        repo = WhatsAppChatRepository(db_session)

        result = await repo.get_least_loaded_user([busy_agent, idle_agent])

        assert result == idle_agent

    async def test_ties_broken_by_lowest_string_id(self, db_session, make_real_user_id):
        """Sin hilos asignados a ninguno, ambos empatan en 0 -- gana el de id menor
        en orden de string (orden estable documentado en el repo)."""
        agent_a = await make_real_user_id()
        agent_b = await make_real_user_id()
        repo = WhatsAppChatRepository(db_session)

        expected = min([agent_a, agent_b], key=str)
        result = await repo.get_least_loaded_user([agent_a, agent_b])

        assert result == expected

    async def test_soft_deleted_chats_do_not_count_toward_load(self, db_session, real_org, make_real_user_id):
        agent = await make_real_user_id()
        idle_agent = await make_real_user_id()
        chat = build_chat(real_org.id, assigned_user_id=agent)
        db_session.add(chat)
        await db_session.flush()
        repo = WhatsAppChatRepository(db_session)
        await repo.delete(chat)

        result = await repo.get_least_loaded_user([agent, idle_agent])

        # Ambos en 0 tras el soft-delete -- desempate por id menor.
        assert result == min([agent, idle_agent], key=str)
