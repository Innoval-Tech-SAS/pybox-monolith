import uuid
from typing import Annotated

from fastapi import File, Form, Query, UploadFile

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from messaging.bulk_send.dependencies import BulkSendServiceDep
from messaging.bulk_send.schemas.bulk_send_schemas import BulkSendResponse
from messaging.bulk_send.utils.file_parser import parse_file

router = APIRouter(prefix="/messaging/bulk-send", tags=["Envío masivo"])


@router.post(
    "/",
    response_model=BulkSendResponse,
    summary="Envío masivo desde archivo CSV o Excel",
)
async def bulk_send(
    session: CurrentSession,
    service: BulkSendServiceDep,
    file: Annotated[UploadFile, File(description="Archivo CSV o XLSX con columnas: tipo_documento, documento, destinatario + variables")],
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
    channel_id: Annotated[uuid.UUID, Query(alias="channelId")],
    template_id: Annotated[uuid.UUID | None, Query(alias="templateId")] = None,
    body: Annotated[str | None, Form(description="Contenido del mensaje con variables {nombre_columna}. Requerido si no se usa templateId")] = None,
    subject: Annotated[str | None, Form(description="Asunto del mensaje. Obligatorio para EMAIL")] = None,
) -> BulkSendResponse:
    rows = await parse_file(file)
    return await service.process(
        portfolio_id=portfolio_id,
        channel_id=channel_id,
        rows=rows,
        user_session=session,
        template_id=template_id,
        body=body,
        subject=subject,
    )
 