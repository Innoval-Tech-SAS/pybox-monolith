"""Test de integración HTTP de `POST /portfolios/upload-csv/installments`.

De paso valida el patrón de sesión propia del background task
(`installments_and_notify`, en `installment_background_tasks.py`): el fixture
`client` parchea `db.get_session` para que el task vea, dentro de la MISMA
transacción del test, el crédito insertado por `real_credit` -- si el task usara la
sesión de la request (cerrada antes de que BackgroundTasks corra) o abriera una
sesión desconectada de la transacción del test, no encontraría el crédito y la
carga terminaría en 0 procesados.
"""

import uuid

from identity.organizations.enums.organization_enums import VerificationStatus
from identity.users.enums.user_enums import UserRole, UserScope
from receivables.payments.repository.payment_repository import PaymentRepository
from tests.receivables.conftest import build_organization, build_portfolio

BASE = "/api/v1/portfolios"


def installment_csv_bytes(credit_number: str) -> bytes:
    from tests.receivables.conftest import build_installments_csv

    return build_installments_csv(
        [
            {
                "Numero de credito": credit_number,
                "Numero de la cuota que se cancela": "1",
                "Pago total del credito": "no",
                "Fecha limite de pago": "01/01/2026",
                "Fecha del pago": "",
                "total": "100000",
                "abono a capital": "80000",
                "interes corriente": "20000",
                "interes mora": "0",
                "Seguro de vida": "0",
                "seguro de vehiculo": "0",
                "otros cargos": "0",
                "IVA": "0",
                "Comision": "0",
                "Plataforma": "0",
            }
        ]
    )


class TestUploadInstallments:
    async def test_valid_creates_a_payment_via_the_background_task(
        self,
        auth_as,
        make_user_session_factory,
        real_credit,
        db_session,
        real_admin_user_id,
    ):
        # user_id real: el background task notifica al usuario que subió el archivo,
        # y esa fila necesita una FK válida a `usuarios` (ver notificaciones_id_usuario_fkey).
        authed = auth_as(
            make_user_session_factory(
                user_id=real_admin_user_id, role=UserRole.ADMIN, scope=UserScope.GLOBAL
            )
        )
        resp = await authed.post(
            f"{BASE}/upload-csv/installments",
            params={"portfolioId": str(real_credit.portfolio_id)},
            files={
                "file": (
                    "cuotas.csv",
                    installment_csv_bytes(real_credit.credit_number),
                    "text/csv",
                )
            },
        )
        assert resp.status_code == 202

        # El task corre en su propia sesión (ver installment_background_tasks.py),
        # pero `client` la parchea a la MISMA `db_session` del test -- si esto
        # rompiera, el pago no aparecería porque el task no vería el crédito
        # insertado por el fixture `real_credit` en esta misma transacción.
        payment = await PaymentRepository(db_session).get_by_credit_and_installment(
            real_credit.id, 1
        )
        assert payment is not None
        assert payment.payment_amount == 100000

    async def test_portfolio_not_found_returns_404(
        self, auth_as, make_user_session_factory
    ):
        authed = auth_as(
            make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL)
        )
        resp = await authed.post(
            f"{BASE}/upload-csv/installments",
            params={"portfolioId": str(uuid.uuid4())},
            files={"file": ("cuotas.csv", installment_csv_bytes("CR-X"), "text/csv")},
        )
        assert resp.status_code == 404

    async def test_invalid_extension_returns_400(
        self, auth_as, make_user_session_factory, real_portfolio
    ):
        authed = auth_as(
            make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL)
        )
        resp = await authed.post(
            f"{BASE}/upload-csv/installments",
            params={"portfolioId": str(real_portfolio.id)},
            files={"file": ("cuotas.txt", b"contenido", "text/plain")},
        )
        assert resp.status_code == 400

    async def test_without_auth_returns_401(self, client, real_portfolio):
        resp = await client.post(
            f"{BASE}/upload-csv/installments",
            params={"portfolioId": str(real_portfolio.id)},
            files={"file": ("cuotas.csv", installment_csv_bytes("CR-X"), "text/csv")},
        )
        assert resp.status_code == 401

    async def test_unverified_org_returns_403(
        self, db_session, auth_as, make_user_session_factory
    ):
        """Regresión para la Fase 3c de la auditoría: este endpoint también pasó de
        `OrganizationRepository` directo a `OrganizationService.ensure_verified`."""
        org = build_organization(verification_status=VerificationStatus.PENDING)
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()

        authed = auth_as(
            make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL)
        )
        resp = await authed.post(
            f"{BASE}/upload-csv/installments",
            params={"portfolioId": str(portfolio.id)},
            files={"file": ("cuotas.csv", installment_csv_bytes("CR-X"), "text/csv")},
        )
        assert resp.status_code == 403
