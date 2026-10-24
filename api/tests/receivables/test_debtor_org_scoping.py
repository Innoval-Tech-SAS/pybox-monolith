"""El deudor pertenece a UNA organización.

Antes era global (unique por hash de documento): la carga de una empresa sobrescribía el
nombre del deudor de otra y le exponía sus direcciones/contactos. Aquí se fija el nuevo
contrato: el mismo documento en dos empresas son dos filas independientes, cada carga y
cada consulta queda acotada a su organización, y el titular (scope SELF) sigue viendo sus
obligaciones de todas las empresas.
"""

import pytest
from fastapi import HTTPException

from app_platform.documents.repository.document_repository import DocumentRepository
from core.security.constants.permissions import PORTFOLIO_CLIENTS
from core.security.services.encrypt_service import encrypt_service
from identity.organizations.enums.organization_enums import VerificationStatus
from identity.users.enums.user_enums import (
    IdentityVerificationStatus,
    UserRole,
    UserScope,
)
from identity.users.schemas.user_session_schema import OrgSessionEntry
from receivables.contact_methods.repository.contact_method_repository import (
    ContactMethodRepository,
)
from receivables.credits.repository.credit_repository import CreditRepository
from receivables.credits.services.my_credits_service import MyCreditsService
from receivables.debtors.enums.debtor_enums import DebtorType
from receivables.debtors.repository.address_repository import AddressRepository
from receivables.debtors.repository.debtor_repository import DebtorRepository
from receivables.debtors.schemas.debtor_schemas import CreateDebtorRequest
from receivables.debtors.services.debtor_service import DebtorService
from receivables.payments.repository.payment_repository import PaymentRepository
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository
from receivables.portfolios.services.portfolio_csv_service import PortfolioCsvService
from tests.factories import unique_document_number
from tests.receivables.conftest import (
    add_organization,
    build_credit,
    build_debtor,
    build_portfolio,
    build_portfolio_csv,
    portfolio_csv_row,
)


def build_debtor_service(db_session) -> DebtorService:
    return DebtorService(
        session=db_session,
        debtor_repo=DebtorRepository(db_session),
        address_repo=AddressRepository(db_session),
        contact_repo=ContactMethodRepository(db_session),
        portfolio_repo=PortfolioRepository(db_session),
        credit_repo=CreditRepository(db_session),
        payment_repo=PaymentRepository(db_session),
        document_repo=DocumentRepository(db_session),
    )


def org_admin_session(
    make_user_session_factory, org_id, *, permissions=frozenset({PORTFOLIO_CLIENTS})
):
    return make_user_session_factory(
        role=UserRole.ADMIN,
        scope=UserScope.ORGANIZATION,
        orgs={
            str(org_id): OrgSessionEntry(
                role=UserRole.ADMIN,
                org_name="Org",
                verification_status=VerificationStatus.APPROVED,
                permissions=permissions,
            )
        },
    )


@pytest.mark.parametrize("bulk", [False, True], ids=["sequential", "bulk"])
class TestCsvUploadIsScopedToOrganization:
    async def test_same_document_in_two_orgs_creates_two_independent_debtors(
        self, db_session, monkeypatch, bulk
    ):
        if bulk:
            monkeypatch.setenv("PORTFOLIO_CSV_BULK_UPSERT", "true")
        else:
            monkeypatch.delenv("PORTFOLIO_CSV_BULK_UPSERT", raising=False)

        org_a = await add_organization(db_session)
        org_b = await add_organization(db_session)
        document = unique_document_number()
        service = PortfolioCsvService(db_session)

        await service.process_csv(
            build_portfolio_csv(
                [
                    portfolio_csv_row(
                        **{
                            "Numero de documento": document,
                            "Nombre del titular": "Nombre A",
                        }
                    )
                ]
            ),
            organization_id=org_a.id,
            portfolio_name="Portafolio A",
        )
        await service.process_csv(
            build_portfolio_csv(
                [
                    portfolio_csv_row(
                        **{
                            "Numero de documento": document,
                            "Nombre del titular": "Nombre B",
                        }
                    )
                ]
            ),
            organization_id=org_b.id,
            portfolio_name="Portafolio B",
        )

        repo = DebtorRepository(db_session)
        doc_hash = encrypt_service.hash_document(document)
        debtor_a = await repo.get_by_document_number(org_a.id, doc_hash)
        debtor_b = await repo.get_by_document_number(org_b.id, doc_hash)

        assert debtor_a is not None and debtor_b is not None
        assert debtor_a.id != debtor_b.id
        # La carga de B no toca el deudor de A.
        assert debtor_a.full_name == "Nombre A"
        assert debtor_b.full_name == "Nombre B"


class TestDebtorRepositoryScoping:
    async def test_lookup_by_document_number_does_not_cross_organizations(
        self, db_session
    ):
        org_a = await add_organization(db_session)
        org_b = await add_organization(db_session)
        debtor = build_debtor(org_a.id)
        db_session.add(debtor)
        await db_session.flush()

        repo = DebtorRepository(db_session)
        assert (
            await repo.get_by_document_number(org_a.id, debtor.document_number_hash)
            is not None
        )
        assert (
            await repo.get_by_document_number(org_b.id, debtor.document_number_hash)
            is None
        )
        assert (
            await repo.get_by_document_hashes(org_b.id, [debtor.document_number_hash])
            == []
        )

    async def test_list_by_document_returns_one_row_per_organization(self, db_session):
        org_a = await add_organization(db_session)
        org_b = await add_organization(db_session)
        document = unique_document_number()
        in_a = build_debtor(org_a.id, document_number_plain=document)
        in_b = build_debtor(org_b.id, document_number_plain=document)
        db_session.add_all([in_a, in_b])
        await db_session.flush()

        rows = await DebtorRepository(db_session).list_by_document(
            "CC", encrypt_service.hash_document(document)
        )

        assert {d.id for d in rows} == {in_a.id, in_b.id}


class TestCreateDebtorIsScopedToOrganization:
    @staticmethod
    def _request(org_id, document: str) -> CreateDebtorRequest:
        return CreateDebtorRequest(
            organization_id=org_id,
            full_name="Deudor Nuevo",
            debtor_type=DebtorType.DEBTOR,
            document_type="CC",
            document_number=document,
        )

    async def test_without_permission_on_target_org_raises_403(
        self, db_session, make_user_session_factory
    ):
        org_a = await add_organization(db_session)
        org_b = await add_organization(db_session)
        session = org_admin_session(make_user_session_factory, org_a.id)

        with pytest.raises(HTTPException) as exc_info:
            await build_debtor_service(db_session).create_debtor(
                self._request(org_b.id, unique_document_number()), session
            )
        assert exc_info.value.status_code == 403

    async def test_duplicate_in_same_org_raises_409(
        self, db_session, make_user_session_factory
    ):
        org = await add_organization(db_session)
        session = org_admin_session(make_user_session_factory, org.id)
        service = build_debtor_service(db_session)
        document = unique_document_number()
        await service.create_debtor(self._request(org.id, document), session)

        with pytest.raises(HTTPException) as exc_info:
            await service.create_debtor(self._request(org.id, document), session)
        assert exc_info.value.status_code == 409

    async def test_document_existing_in_another_org_is_not_a_conflict(
        self, db_session, make_user_session_factory
    ):
        """El 409 no debe delatar que otra empresa ya tiene a esa persona."""
        org_a = await add_organization(db_session)
        org_b = await add_organization(db_session)
        document = unique_document_number()
        db_session.add(build_debtor(org_a.id, document_number_plain=document))
        await db_session.flush()

        created = await build_debtor_service(db_session).create_debtor(
            self._request(org_b.id, document),
            org_admin_session(make_user_session_factory, org_b.id),
        )

        assert created.organization_id == org_b.id


class TestSelfServiceSpansOrganizations:
    async def test_my_credits_lists_credits_from_every_organization(self, db_session):
        document = unique_document_number()
        credits = []
        for _ in range(2):
            org = await add_organization(db_session)
            portfolio = build_portfolio(org.id)
            db_session.add(portfolio)
            debtor = build_debtor(org.id, document_number_plain=document)
            db_session.add(debtor)
            await db_session.flush()
            credit = build_credit(portfolio.id, debtor.id)
            db_session.add(credit)
            await db_session.flush()
            credits.append(credit)

        result = await MyCreditsService(db_session).get_my_credits(
            "CC",
            encrypt_service.hash_document(document),
            IdentityVerificationStatus.APPROVED,
        )

        assert {c.id for c in result} == {c.id for c in credits}

    async def test_credit_of_a_deleted_portfolio_is_hidden_instead_of_failing(
        self, db_session
    ):
        """Antes reventaba con KeyError: el portafolio dado de baja no aparecía en el mapa."""
        org = await add_organization(db_session)
        document = unique_document_number()
        debtor = build_debtor(org.id, document_number_plain=document)
        live_portfolio = build_portfolio(org.id)
        dead_portfolio = build_portfolio(org.id)
        db_session.add_all([debtor, live_portfolio, dead_portfolio])
        await db_session.flush()
        live_credit = build_credit(live_portfolio.id, debtor.id)
        dead_credit = build_credit(dead_portfolio.id, debtor.id)
        db_session.add_all([live_credit, dead_credit])
        await db_session.flush()
        await PortfolioRepository(db_session).delete(dead_portfolio)

        result = await MyCreditsService(db_session).get_my_credits(
            "CC",
            encrypt_service.hash_document(document),
            IdentityVerificationStatus.APPROVED,
        )

        assert [c.id for c in result] == [live_credit.id]
