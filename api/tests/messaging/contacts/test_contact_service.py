"""Tests de `ContactService.get_by_debtor` (historial de envíos de un deudor,
agrupado por canal, ver contact_service.py). Riesgo real: el cálculo de
`total_pages` con `ceil` -- un grupo sin envíos (`total=0`) debe reportar 1 página, no
0 (rompería un frontend que itera `range(1, total_pages + 1)`), y con envíos debe
redondear hacia arriba, no truncar.

Unitario puro: `ContactRepository`/`PortfolioRepository` van mockeados.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

from messaging.contacts.services.contact_service import ContactService


def build_service():
    repo = MagicMock()
    portfolio_repo = MagicMock()
    return ContactService(repo, portfolio_repo), repo, portfolio_repo


def make_user_session():
    session = MagicMock()
    session.is_global = True
    return session


class TestGetByDebtorPagination:
    async def test_zero_total_reports_one_page_not_zero(self):
        service, repo, portfolio_repo = build_service()
        portfolio = MagicMock(organization_id=uuid.uuid4())
        portfolio_repo.get_by_id = AsyncMock(return_value=portfolio)
        repo.get_by_debtor_grouped_paginated = AsyncMock(
            return_value=[(uuid.uuid4(), "SMS", 0, [])]
        )

        groups = await service.get_by_debtor(uuid.uuid4(), uuid.uuid4(), make_user_session(), page=1, page_size=10)

        assert groups[0].total_pages == 1

    async def test_total_pages_rounds_up_for_partial_last_page(self):
        service, repo, portfolio_repo = build_service()
        portfolio = MagicMock(organization_id=uuid.uuid4())
        portfolio_repo.get_by_id = AsyncMock(return_value=portfolio)
        repo.get_by_debtor_grouped_paginated = AsyncMock(
            return_value=[(uuid.uuid4(), "EMAIL", 11, [])]
        )

        groups = await service.get_by_debtor(uuid.uuid4(), uuid.uuid4(), make_user_session(), page=1, page_size=5)

        # 11 items / 5 por página = 2.2 -> 3 páginas, no 2 (truncado).
        assert groups[0].total_pages == 3

    async def test_multiple_channel_groups_are_all_returned(self):
        service, repo, portfolio_repo = build_service()
        portfolio = MagicMock(organization_id=uuid.uuid4())
        portfolio_repo.get_by_id = AsyncMock(return_value=portfolio)
        repo.get_by_debtor_grouped_paginated = AsyncMock(
            return_value=[
                (uuid.uuid4(), "SMS", 2, []),
                (uuid.uuid4(), "EMAIL", 1, []),
            ]
        )

        groups = await service.get_by_debtor(uuid.uuid4(), uuid.uuid4(), make_user_session(), page=1, page_size=10)

        assert len(groups) == 2
        assert {g.channel_name for g in groups} == {"SMS", "EMAIL"}
