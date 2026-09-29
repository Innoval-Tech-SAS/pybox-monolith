from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from receivables.payment_gateways.services.payment_gateway_credential_management_service import (
    OrganizationGatewayCredentialManagementService,
)


def get_organization_gateway_credential_management_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> OrganizationGatewayCredentialManagementService:
    return OrganizationGatewayCredentialManagementService(session)


OrganizationGatewayCredentialManagementServiceDep = Annotated[
    OrganizationGatewayCredentialManagementService, Depends(get_organization_gateway_credential_management_service)
]
