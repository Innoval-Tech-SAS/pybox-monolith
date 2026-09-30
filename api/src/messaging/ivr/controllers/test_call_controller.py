"""Endpoint de prueba para enviar una llamada IVR única a través de Helena."""

from typing import Any

import httpx
from fastapi import HTTPException, status

from core.config.api_router import APIRouter
from core.config.logger import logger
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_org_or_global
from messaging.ivr.dependencies import HelenaClientDep
from messaging.ivr.schemas.test_call_schemas import IvrTestCallRequest

router = APIRouter(prefix="/ivr/test-call", tags=["IVR - Prueba"])


@router.post("/", summary="Enviar una llamada de prueba de un flujo IVR")
async def send_test_call(
    body: IvrTestCallRequest,
    session: CurrentSession,
    client: HelenaClientDep,
) -> dict[str, Any]:
    require_org_or_global(session)

    payload: dict[str, Any] = {
        "phone": body.phone.strip(),
        "campaignId": body.campaign_id or "TEST",
        "ivrConfig": body.config,
    }
    if body.variables:
        payload["variables"] = body.variables
    if body.customer_name:
        payload["customerName"] = body.customer_name
    if body.customer_document:
        payload["customerDocument"] = body.customer_document
    if body.redial_config:
        payload["redialConfig"] = body.redial_config

    try:
        return await client.send_unique(payload)
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:500] if exc.response is not None else ""
        logger.error(
            "[ivr] test_call_http_error | status=%s body=%s",
            exc.response.status_code if exc.response is not None else "?",
            detail,
        )
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            f"Helena rechazó la llamada de prueba: {detail or exc}",
        ) from exc
    except Exception as exc:  # pylint: disable=broad-exception-caught
        # Cualquier falla no-HTTP de Helena (timeout, conexión) también debe
        # volver como 502 y no como 500 sin manejar.
        logger.error("[ivr] test_call_error | error=%s", exc)
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY, "No se pudo enviar la llamada de prueba."
        ) from exc
