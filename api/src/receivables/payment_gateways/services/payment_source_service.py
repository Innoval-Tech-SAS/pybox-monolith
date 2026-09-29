import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status

from identity.users.schemas.user_session_schema import UserSession
from receivables.payment_gateways.enums.payment_gateway_enums import (
    PaymentSourceType,
    ReceivablesGatewayProvider,
)
from receivables.payment_gateways.gateways.base import WompiPaymentSource
from receivables.payment_gateways.gateways.resolver import ReceivablesGatewayResolver
from receivables.payment_gateways.models.payment_source_model import (
    DebtorPaymentSourceModel,
)
from receivables.payment_gateways.repository.payment_source_repository import (
    DebtorPaymentSourceRepository,
)
from receivables.payment_gateways.utils.wompi_status_mapping import to_source_status
from receivables.payments.services.payment_ownership_resolver import (
    PaymentOwnershipResolver,
)


class PaymentSourceService:
    """Autoservicio del titular: tokeniza un medio de pago (tarjeta o Nequi) y lo
    guarda como fuente reutilizable para cobro futuro de sus cuotas (ver skill
    `wompi-gateway`, Paso 5). PSE y Bancolombia Transfer NO tienen fuente reutilizable
    en Wompi — no aplican aquí, solo al checkout puntual.

    Cada operación se ancla a un `payment_id` propio del titular, solo para resolver
    identidad + organización dueña por la MISMA cadena que el checkout
    (`PaymentOwnershipResolver`, `require_pending=False`: guardar un medio de pago no
    depende de que haya una cuota vencida en ese momento). Es una limitación de alcance
    consciente para esta tarea — no hay todavía un endpoint de "mis métodos de pago
    automático" independiente de una cuota puntual."""

    def __init__(
        self,
        ownership_resolver: PaymentOwnershipResolver,
        source_repo: DebtorPaymentSourceRepository,
        gateway_resolver: ReceivablesGatewayResolver,
    ) -> None:
        self._ownership_resolver = ownership_resolver
        self._source_repo = source_repo
        self._gateway_resolver = gateway_resolver

    async def _resolve_debtor_and_org(
        self, session: UserSession, payment_id: uuid.UUID
    ) -> tuple[uuid.UUID, uuid.UUID]:
        (
            _payment,
            credit,
            portfolio,
        ) = await self._ownership_resolver.resolve_owned_payment(
            session, payment_id, require_pending=False
        )
        return credit.debtor_id, portfolio.organization_id

    async def create_card_source(
        self,
        session: UserSession,
        payment_id: uuid.UUID,
        number: str,
        cvc: str,
        exp_month: str,
        exp_year: str,
        card_holder: str,
        customer_email: str,
    ) -> DebtorPaymentSourceModel:
        debtor_id, organization_id = await self._resolve_debtor_and_org(
            session, payment_id
        )
        gateway = await self._require_gateway(organization_id)
        tokens = await gateway.get_acceptance_tokens()
        token = await gateway.tokenize_card(
            number, cvc, exp_month, exp_year, card_holder
        )
        source = await gateway.create_payment_source(
            type="CARD",
            token=token,
            customer_email=customer_email,
            acceptance_token=tokens.acceptance_token,
            accept_personal_auth=tokens.personal_data_token,
        )
        return await self._persist_source(debtor_id, PaymentSourceType.CARD, source)

    async def create_nequi_source(
        self,
        session: UserSession,
        payment_id: uuid.UUID,
        phone_number: str,
        customer_email: str,
    ) -> DebtorPaymentSourceModel:
        debtor_id, organization_id = await self._resolve_debtor_and_org(
            session, payment_id
        )
        gateway = await self._require_gateway(organization_id)
        tokens = await gateway.get_acceptance_tokens()
        token = await gateway.tokenize_nequi(phone_number)
        source = await gateway.create_payment_source(
            type="NEQUI",
            token=token,
            customer_email=customer_email,
            acceptance_token=tokens.acceptance_token,
            accept_personal_auth=tokens.personal_data_token,
        )
        return await self._persist_source(debtor_id, PaymentSourceType.NEQUI, source)

    async def list_active(
        self, session: UserSession, payment_id: uuid.UUID
    ) -> list[DebtorPaymentSourceModel]:
        debtor_id, _organization_id = await self._resolve_debtor_and_org(
            session, payment_id
        )
        return await self._source_repo.list_active_by_debtor_id(debtor_id)

    async def revoke(
        self, session: UserSession, payment_id: uuid.UUID, source_id: uuid.UUID
    ) -> None:
        debtor_id, _organization_id = await self._resolve_debtor_and_org(
            session, payment_id
        )
        source = await self._source_repo.get_by_id(source_id)
        # 404 genérico (no 403): que un deudor confirme la existencia de una fuente de
        # pago de otro deudor por el código de error ya es una fuga de información.
        if source is None or source.debtor_id != debtor_id:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "Fuente de pago no encontrada."
            )
        source.is_active = False
        await self._source_repo.update(source)

    async def _require_gateway(self, organization_id: uuid.UUID):
        gateway = await self._gateway_resolver.get_for_organization(
            organization_id, ReceivablesGatewayProvider.WOMPI
        )
        if gateway is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Esta organización no tiene una pasarela de pago configurada.",
            )
        return gateway

    async def _persist_source(
        self,
        debtor_id: uuid.UUID,
        source_type: PaymentSourceType,
        source: WompiPaymentSource,
    ) -> DebtorPaymentSourceModel:
        model = DebtorPaymentSourceModel(
            debtor_id=debtor_id,
            provider=ReceivablesGatewayProvider.WOMPI,
            type=source_type,
            provider_source_id=source.id,
            status=to_source_status(source.status),
            accepted_at=datetime.now(timezone.utc),
        )
        return await self._source_repo.add(model)
