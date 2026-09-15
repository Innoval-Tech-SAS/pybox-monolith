import uuid

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from messaging.whatsapp.dependencies import WhatsAppCredentialsServiceDep
from messaging.whatsapp.schemas.whatsapp_credentials_schemas import (
    WhatsAppOrgCredentialsRequest,
    WhatsAppOrgCredentialsResponse,
)

router = APIRouter(prefix="/organizations/{organization_id}/whatsapp-credentials", tags=["Credenciales de WhatsApp"])


@router.get("", response_model=WhatsAppOrgCredentialsResponse, summary="Obtener el número de WhatsApp de la organización")
async def get_whatsapp_credentials(
    organization_id: uuid.UUID,
    session: CurrentSession,
    service: WhatsAppCredentialsServiceDep,
) -> WhatsAppOrgCredentialsResponse:
    credentials = await service.get(organization_id, session)
    return WhatsAppOrgCredentialsResponse.model_validate(credentials)


@router.put("", response_model=WhatsAppOrgCredentialsResponse, summary="Configurar el número de WhatsApp de la organización")
async def upsert_whatsapp_credentials(
    organization_id: uuid.UUID,
    body: WhatsAppOrgCredentialsRequest,
    session: CurrentSession,
    service: WhatsAppCredentialsServiceDep,
) -> WhatsAppOrgCredentialsResponse:
    credentials = await service.upsert(organization_id, body, session)
    return WhatsAppOrgCredentialsResponse.model_validate(credentials)
