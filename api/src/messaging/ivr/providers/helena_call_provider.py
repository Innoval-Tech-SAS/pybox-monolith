"""Adaptador de Helena para el envío masivo de llamadas IVR."""

from __future__ import annotations

from typing import Any

import httpx

from core.config.logger import logger
from messaging.ivr.client.helena_client import HelenaClient
from messaging.ivr.config.helena_config import load_helena_config


class HelenaCallProvider:
    """Adapta el motor de campañas del template a la API bulk-json de Helena.

    Construye el payload `MakeBulkOutboundCallsDto` (phones[] + ivrConfig +
    redialConfig) y lo envía en una única petición `POST /calls/bulk`. La
    configuración de Helena se carga de forma perezosa en el primer envío para
    no exigir las variables de entorno cuando la instalación no usa IVR.
    """

    def __init__(self) -> None:
        self._client: HelenaClient | None = None

    def _get_client(self) -> HelenaClient:
        if self._client is None:
            self._client = HelenaClient(load_helena_config())
        return self._client

    async def send_bulk(
        self,
        *,
        targets: list[dict[str, Any]],
        ivr_config: dict[str, Any],
        campaign_id: str,
        redial_config: dict[str, Any] | None = None,
        caller_id: str | None = None,
        default_variables: dict[str, Any] | None = None,
        ivr_flow_id: str | None = None,
        calls_per_second: int | None = None,
        max_concurrent: int | None = None,
        contact_policy_id: str | None = None,
    ) -> tuple[bool, dict[str, str] | None, str | None]:
        """Envía el bulk de llamadas. Devuelve (ok, ids_by_recipient, sending_id).

        `sending_id` es el `bulkId` de Helena (agrupa la ejecución en su cola).
        Helena no retorna ids por teléfono de forma síncrona, así que
        `ids_by_recipient` es None (se resolverá vía webhook en una fase futura).
        """
        phones: list[dict[str, Any]] = []
        for t in targets:
            phone = str(t.get("phone") or "").strip()
            if not phone:
                continue
            entry: dict[str, Any] = {"phone": phone}
            if t.get("document"):
                entry["customerDocument"] = str(t["document"])
            if t.get("name"):
                entry["customerName"] = str(t["name"])
            if t.get("variables"):
                entry["variables"] = t["variables"]
            if ivr_flow_id:
                # Solo viaja el id del flujo, no el mapa de etiquetas: duplicarlo
                # en cada fila de un bulk de miles sería absurdo, y releerlo al
                # recibir el webhook permite corregir las etiquetas sin reenviar.
                # Mismo criterio que `collect_send_masivos` con su `ivrConfigId`.
                entry["customFields"] = {"ivrFlowId": ivr_flow_id}
            phones.append(entry)

        if not phones:
            return False, None, None

        payload: dict[str, Any] = {
            "phones": phones,
            "defaultCampaignId": campaign_id,
            "ivrConfig": ivr_config,
        }
        if caller_id:
            payload["defaultCallerId"] = caller_id
        if redial_config:
            payload["redialConfig"] = redial_config
        if default_variables:
            payload["defaultVariables"] = default_variables
        if calls_per_second is not None:
            payload["callsPerSecond"] = calls_per_second
        if max_concurrent is not None:
            payload["maxConcurrent"] = max_concurrent
        if contact_policy_id:
            payload["contactPolicyId"] = contact_policy_id

        try:
            # scheduled_date/time vacíos: el template ya disparó a la hora correcta,
            # Helena procesa el bulk de inmediato.
            body = await self._get_client().send_bulk_json(payload)
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:500] if exc.response is not None else ""
            logger.error(
                "[helena] bulk_http_error | campaign=%s status=%s body=%s",
                campaign_id,
                exc.response.status_code if exc.response is not None else "?",
                detail,
            )
            return False, None, None
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # Cualquier falla no-HTTP (timeout, conexión) degrada igual a
            # "no se pudo enviar" en vez de tumbar el llamador.
            logger.error("[helena] bulk_error | campaign=%s error=%s", campaign_id, exc)
            return False, None, None

        ok = bool(body.get("ok", True)) and bool(body.get("queued", True))
        bulk_id = body.get("bulkId")
        logger.info(
            "[helena] bulk_sent | campaign=%s phones=%d bulk_id=%s queued=%s",
            campaign_id,
            len(phones),
            bulk_id,
            body.get("queuedCount"),
        )
        return ok, None, str(bulk_id) if bulk_id is not None else None
