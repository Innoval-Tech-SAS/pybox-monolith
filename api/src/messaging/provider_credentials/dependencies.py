"""Dependencia de FastAPI para inyectar el MessagingProviderCredentialAdminService."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from messaging.provider_credentials.services.provider_credential_admin_service import (
    MessagingProviderCredentialAdminService,
)


def get_messaging_provider_credential_admin_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> MessagingProviderCredentialAdminService:
    return MessagingProviderCredentialAdminService(session)


MessagingProviderCredentialAdminServiceDep = Annotated[
    MessagingProviderCredentialAdminService,
    Depends(get_messaging_provider_credential_admin_service),
]
