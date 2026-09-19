import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.countries.enums.country_enums import UserDocumentType
from app_platform.countries.repository.country_repository import CountryRepository
from app_platform.support.enums.support_enums import PaymentTopic
from app_platform.support.schemas.support_schemas import SupportFilter
from app_platform.support.services.support_service import SupportService
from core.security.policies.security_policies import get_self_identity
from identity.users.schemas.user_session_schema import UserSession
from receivables.credits.repository.credit_repository import CreditRepository
from receivables.debtors.repository.debtor_repository import DebtorRepository
from receivables.payments.enums.payment_enums import PaymentStatus
from receivables.payments.models.payment_model import PaymentModel
from receivables.payments.models.payment_ticket_model import PaymentTicketModel
from receivables.payments.repository.payment_repository import PaymentRepository
from receivables.payments.repository.payment_ticket_repository import PaymentTicketRepository
from receivables.payments.schemas.payment_selfservice_schemas import PaymentRequestResponse
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository

_RESCHEDULE_WINDOW_DAYS = 30


class PaymentSelfServiceService:
    """Autogestión del titular (rol USER, scope SELF) sobre una cuota desde el
    calendario financiero: solicitar reprogramación o validar un pago con comprobante.
    Ambas crean un ticket asignado al CUSTOMER_SERVICE de la organización dueña."""

    def __init__(self, session: AsyncSession) -> None:
        self._debtor_repo = DebtorRepository(session)
        self._credit_repo = CreditRepository(session)
        self._payment_repo = PaymentRepository(session)
        self._portfolio_repo = PortfolioRepository(session)
        self._payment_ticket_repo = PaymentTicketRepository(session)
        self._support = SupportService(session)
        self._country_repo = CountryRepository(session)

    async def request_reschedule(
        self, session: UserSession, payment_id: uuid.UUID, new_date: datetime
    ) -> PaymentRequestResponse:
        payment, credit, org_id, tz = await self._resolve_owned_payment(session, payment_id)
        self._validate_reschedule_date(new_date, tz)

        ticket = await self._support.create_payment_ticket(
            org_id=org_id,
            created_by=session.user_id,
            topic=PaymentTopic.PAYMENT_RESCHEDULE,
            title=f"Reprogramación de pago · crédito {credit.credit_number}",
            notes=(
                f"El titular solicita reprogramar la cuota "
                f"#{payment.installment_number or payment.id} del crédito {credit.credit_number} "
                f"para el {new_date.date().isoformat()}."
            ),
        )
        await self._payment_ticket_repo.add(
            PaymentTicketModel(
                ticket_id=ticket.id,
                payment_id=payment.id,
                credit_id=credit.id,
                requested_date=new_date,
            )
        )
        payment.status = PaymentStatus.RESCHEDULE_REQUESTED
        await self._payment_repo.update(payment)

        return PaymentRequestResponse(
            ticket_number=ticket.ticket_number, payment_status=payment.status.value
        )

    async def request_validation(
        self, session: UserSession, payment_id: uuid.UUID, files: list[UploadFile]
    ) -> PaymentRequestResponse:
        if not files:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Adjunta al menos un comprobante.")

        payment, credit, org_id, _tz = await self._resolve_owned_payment(session, payment_id)

        ticket = await self._support.create_payment_ticket(
            org_id=org_id,
            created_by=session.user_id,
            topic=PaymentTopic.PAYMENT_VALIDATION,
            title=f"Validación de pago · crédito {credit.credit_number}",
            notes=(
                f"El titular reporta haber pagado la cuota "
                f"#{payment.installment_number or payment.id} del crédito {credit.credit_number} "
                f"y adjunta comprobante."
            ),
        )

        # El comprobante queda en el almacén de objetos como adjunto del ticket,
        # reutilizando la validación de extensión/tamaño existente.
        upload_filter = SupportFilter(created_by=session.user_id, can_create=True)
        await self._support.upload_attachments(ticket.ticket_number, files, upload_filter)

        await self._payment_ticket_repo.add(
            PaymentTicketModel(
                ticket_id=ticket.id,
                payment_id=payment.id,
                credit_id=credit.id,
            )
        )
        payment.status = PaymentStatus.VALIDATION_REQUESTED
        await self._payment_repo.update(payment)

        return PaymentRequestResponse(
            ticket_number=ticket.ticket_number, payment_status=payment.status.value
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _resolve_owned_payment(
        self, session: UserSession, payment_id: uuid.UUID
    ) -> tuple[PaymentModel, object, uuid.UUID, ZoneInfo]:
        doc_type_str, doc_number_hash = get_self_identity(session)
        try:
            doc_type = UserDocumentType(doc_type_str)
        except ValueError:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Documento de identidad inválido.")

        debtor = await self._debtor_repo.get_by_document(doc_type, doc_number_hash)
        if debtor is None:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No se encontró tu registro de deudor.")

        payment = await self._payment_repo.get_by_id(payment_id)
        if payment is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Pago no encontrado.")

        credit = await self._credit_repo.get_by_id(payment.credit_id)
        # 404 genérico también cuando el pago existe pero el crédito no es del
        # titular: un 403 distinto de "no encontrado" deja adivinar por fuerza
        # bruta qué IDs de pago existen en el sistema, aunque sean de otro deudor.
        if credit is None or debtor.id not in (credit.debtor_id, credit.codebtor_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Pago no encontrado.")

        if payment.status != PaymentStatus.PENDING:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Este pago ya tiene una solicitud en curso o no admite solicitudes.",
            )

        portfolio = await self._portfolio_repo.get_by_id(credit.portfolio_id)
        if portfolio is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Portafolio no encontrado.")

        tz = ZoneInfo(await self._country_repo.get_timezone(portfolio.country)) if portfolio.country else timezone.utc
        return payment, credit, portfolio.organization_id, tz

    @staticmethod
    def _validate_reschedule_date(new_date: datetime, tz) -> None:
        now = datetime.now(tz)
        if new_date.tzinfo is None:
            new_date = new_date.replace(tzinfo=tz)
        if new_date <= now:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "La nueva fecha debe ser futura.")
        if new_date > now + timedelta(days=_RESCHEDULE_WINDOW_DAYS):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"La nueva fecha debe estar dentro de los próximos {_RESCHEDULE_WINDOW_DAYS} días.",
            )
