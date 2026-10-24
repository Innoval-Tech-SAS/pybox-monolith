"""Dependencias de FastAPI para inyectar los servicios de pasarela de pago."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_self
from identity.users.schemas.user_session_schema import UserSession
from receivables.credits.repository.credit_repository import CreditRepository
from receivables.debtors.repository.debtor_repository import DebtorRepository
from receivables.payment_gateways.gateways.resolver import ReceivablesGatewayResolver
from receivables.payment_gateways.repository.payment_attempt_repository import (
    CreditPaymentAttemptRepository,
)
from receivables.payment_gateways.repository.payment_source_repository import (
    DebtorPaymentSourceRepository,
)
from receivables.payment_gateways.services.automatic_charge_service import (
    AutomaticChargeService,
)
from receivables.payment_gateways.services.payment_checkout_service import (
    PaymentCheckoutService,
)
from receivables.payment_gateways.services.payment_gateway_credential_management_service import (  # pylint: disable=line-too-long
    OrganizationGatewayCredentialManagementService,
)
from receivables.payment_gateways.services.payment_gateway_credential_service import (
    OrganizationGatewayCredentialService,
)
from receivables.payment_gateways.services.bold_webhook_service import (
    BoldWebhookService,
)
from receivables.payment_gateways.services.epayco_webhook_service import (
    EpaycoWebhookService,
)
from receivables.payment_gateways.services.payu_webhook_service import (
    PayUWebhookService,
)
from receivables.payment_gateways.services.payment_source_service import (
    PaymentSourceService,
)
from receivables.payment_gateways.services.payment_webhook_service import (
    WompiWebhookService,
)
from receivables.payments.repository.payment_repository import PaymentRepository
from receivables.payments.services.payment_ownership_resolver import (
    PaymentOwnershipResolver,
)
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository


def get_organization_gateway_credential_management_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> OrganizationGatewayCredentialManagementService:
    return OrganizationGatewayCredentialManagementService(session)


def get_receivables_gateway_resolver(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> ReceivablesGatewayResolver:
    return ReceivablesGatewayResolver(OrganizationGatewayCredentialService(session))


def get_payment_ownership_resolver(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> PaymentOwnershipResolver:
    return PaymentOwnershipResolver(
        DebtorRepository(session),
        CreditRepository(session),
        PaymentRepository(session),
        PortfolioRepository(session),
    )


def get_payment_checkout_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
    ownership_resolver: Annotated[
        PaymentOwnershipResolver, Depends(get_payment_ownership_resolver)
    ],
    gateway_resolver: Annotated[
        ReceivablesGatewayResolver, Depends(get_receivables_gateway_resolver)
    ],
) -> PaymentCheckoutService:
    return PaymentCheckoutService(
        ownership_resolver,
        CreditPaymentAttemptRepository(session),
        gateway_resolver,
        PaymentRepository(session),
    )


def get_payment_source_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
    ownership_resolver: Annotated[
        PaymentOwnershipResolver, Depends(get_payment_ownership_resolver)
    ],
    gateway_resolver: Annotated[
        ReceivablesGatewayResolver, Depends(get_receivables_gateway_resolver)
    ],
) -> PaymentSourceService:
    return PaymentSourceService(
        ownership_resolver, DebtorPaymentSourceRepository(session), gateway_resolver
    )


def get_wompi_webhook_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
    gateway_resolver: Annotated[
        ReceivablesGatewayResolver, Depends(get_receivables_gateway_resolver)
    ],
) -> WompiWebhookService:
    return WompiWebhookService(
        gateway_resolver,
        CreditPaymentAttemptRepository(session),
        PaymentRepository(session),
    )


def get_bold_webhook_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
    gateway_resolver: Annotated[
        ReceivablesGatewayResolver, Depends(get_receivables_gateway_resolver)
    ],
) -> BoldWebhookService:
    return BoldWebhookService(
        OrganizationGatewayCredentialService(session),
        gateway_resolver,
        CreditPaymentAttemptRepository(session),
        PaymentRepository(session),
    )


def get_epayco_webhook_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
    gateway_resolver: Annotated[
        ReceivablesGatewayResolver, Depends(get_receivables_gateway_resolver)
    ],
) -> EpaycoWebhookService:
    return EpaycoWebhookService(
        gateway_resolver,
        CreditPaymentAttemptRepository(session),
        PaymentRepository(session),
    )


def get_payu_webhook_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
    gateway_resolver: Annotated[
        ReceivablesGatewayResolver, Depends(get_receivables_gateway_resolver)
    ],
) -> PayUWebhookService:
    return PayUWebhookService(
        gateway_resolver,
        CreditPaymentAttemptRepository(session),
        PaymentRepository(session),
    )


def get_automatic_charge_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
    gateway_resolver: Annotated[
        ReceivablesGatewayResolver, Depends(get_receivables_gateway_resolver)
    ],
) -> AutomaticChargeService:
    """Sin sesión de usuario: pensada para un cron futuro, no para un endpoint HTTP —
    ver `AutomaticChargeService`. Expuesta aquí igual por si un futuro endpoint admin
    necesita disparar un cobro puntual a mano."""
    return AutomaticChargeService(
        PaymentRepository(session),
        CreditRepository(session),
        PortfolioRepository(session),
        DebtorPaymentSourceRepository(session),
        CreditPaymentAttemptRepository(session),
        gateway_resolver,
    )


def require_self_session_for_payment_gateways(session: CurrentSession) -> UserSession:
    """Gate de scope SELF a nivel de ruta: rechaza en el borde a quien no sea el
    titular, antes de instanciar el service. La política pura vive en
    security_policies."""
    require_self(session)
    return session


OrganizationGatewayCredentialManagementServiceDep = Annotated[
    OrganizationGatewayCredentialManagementService,
    Depends(get_organization_gateway_credential_management_service),
]
PaymentCheckoutServiceDep = Annotated[
    PaymentCheckoutService, Depends(get_payment_checkout_service)
]
PaymentSourceServiceDep = Annotated[
    PaymentSourceService, Depends(get_payment_source_service)
]
WompiWebhookServiceDep = Annotated[
    WompiWebhookService, Depends(get_wompi_webhook_service)
]
BoldWebhookServiceDep = Annotated[BoldWebhookService, Depends(get_bold_webhook_service)]
EpaycoWebhookServiceDep = Annotated[
    EpaycoWebhookService, Depends(get_epayco_webhook_service)
]
PayUWebhookServiceDep = Annotated[PayUWebhookService, Depends(get_payu_webhook_service)]
AutomaticChargeServiceDep = Annotated[
    AutomaticChargeService, Depends(get_automatic_charge_service)
]
RequireSelfForPaymentGateways = Annotated[
    UserSession, Depends(require_self_session_for_payment_gateways)
]
