from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from billing.provider_credentials.services.provider_credential_admin_service import (
    PlatformGatewayCredentialAdminService,
)


def get_platform_gateway_credential_admin_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> PlatformGatewayCredentialAdminService:
    return PlatformGatewayCredentialAdminService(session)


PlatformGatewayCredentialAdminServiceDep = Annotated[
    PlatformGatewayCredentialAdminService, Depends(get_platform_gateway_credential_admin_service)
]
