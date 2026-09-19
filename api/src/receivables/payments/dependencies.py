from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_self
from identity.users.schemas.user_session_schema import UserSession
from receivables.payments.services.payment_catalog_service import PaymentCatalogService
from receivables.payments.services.payment_selfservice_service import PaymentSelfServiceService


def get_payment_catalog_service() -> PaymentCatalogService:
    """Sin sesión de BD: el catálogo se arma desde el enum."""
    return PaymentCatalogService()


def get_payment_selfservice_service(
    db: Annotated[AsyncSession, Depends(get_main_session)],
) -> PaymentSelfServiceService:
    return PaymentSelfServiceService(db)


def require_self_session(session: CurrentSession) -> UserSession:
    """Gate de scope SELF a nivel de ruta: rechaza en el borde a quien no sea el
    titular, antes de instanciar el service. La política pura vive en security_policies."""
    require_self(session)
    return session


PaymentCatalogServiceDep = Annotated[PaymentCatalogService, Depends(get_payment_catalog_service)]
PaymentSelfServiceServiceDep = Annotated[
    PaymentSelfServiceService, Depends(get_payment_selfservice_service)
]
RequireSelf = Annotated[UserSession, Depends(require_self_session)]
