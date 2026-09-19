from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from app_platform.provider_credentials.services.provider_credential_admin_service import (
    ProviderCredentialAdminService,
)


def get_provider_credential_admin_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> ProviderCredentialAdminService:
    return ProviderCredentialAdminService(session)


ProviderCredentialAdminServiceDep = Annotated[
    ProviderCredentialAdminService, Depends(get_provider_credential_admin_service)
]
