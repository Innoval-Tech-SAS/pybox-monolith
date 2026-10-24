"""Dependencias de FastAPI para inyectar los servicios de créditos."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_self
from identity.users.schemas.user_session_schema import UserSession
from receivables.credits.services.credit_catalog_service import CreditCatalogService
from receivables.credits.services.credit_selfservice_service import (
    CreditSelfServiceService,
)
from receivables.credits.services.my_credits_service import MyCreditsService


def get_credit_catalog_service() -> CreditCatalogService:
    """Sin sesión de BD: el catálogo se arma desde los enums."""
    return CreditCatalogService()


def get_my_credits_service(
    db: Annotated[AsyncSession, Depends(get_main_session)],
) -> MyCreditsService:
    return MyCreditsService(db)


def get_credit_selfservice_service(
    db: Annotated[AsyncSession, Depends(get_main_session)],
) -> CreditSelfServiceService:
    return CreditSelfServiceService(db)


def require_self_session(session: CurrentSession) -> UserSession:
    """Gate de scope SELF a nivel de ruta: rechaza en el borde a quien no sea el
    titular, antes de instanciar el service. La política pura vive en
    security_policies."""
    require_self(session)
    return session


CreditCatalogServiceDep = Annotated[
    CreditCatalogService, Depends(get_credit_catalog_service)
]
MyCreditsServiceDep = Annotated[MyCreditsService, Depends(get_my_credits_service)]
CreditSelfServiceServiceDep = Annotated[
    CreditSelfServiceService, Depends(get_credit_selfservice_service)
]
RequireSelf = Annotated[UserSession, Depends(require_self_session)]
