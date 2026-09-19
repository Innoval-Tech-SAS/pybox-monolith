"""Registro idempotente del webhook de Pybox en Helena.

Se ejecuta en el arranque de la API. Si Helena no responde, o si la instalación
no usa el canal IVR, se registra un aviso y se sigue: el arranque de la API
nunca debe depender de un servicio externo.
"""

from __future__ import annotations

from typing import Any

from core.config.logger import logger
from core.tools.config_tools import get_or_default
from messaging.ivr.client.helena_client import HelenaClient
from messaging.ivr.config.helena_config import load_helena_config
from messaging.ivr.constants.helena_defaults import UNSET
from messaging.ivr.enums.ivr_enums import SUBSCRIBED_EVENTS

_DESCRIPTION = "Pybox — resultados de llamadas IVR"


async def ensure_webhook_registered() -> None:
    """Crea o actualiza el webhook de Pybox en Helena.

    Requiere `HELENA_PUBLIC_WEBHOOK_URL` (la URL pública de este endpoint) y
    `HELENA_WEBHOOK_SECRET` (el secreto con el que Helena firmará los eventos).
    Sin cualquiera de las dos, no hace nada.
    """
    public_url = get_or_default("HELENA_PUBLIC_WEBHOOK_URL", UNSET).strip()
    if not public_url:
        logger.info("[ivr_webhook] HELENA_PUBLIC_WEBHOOK_URL no definida: no se registra webhook")
        return

    secret = get_or_default("HELENA_WEBHOOK_SECRET", UNSET).strip()
    if not secret:
        logger.error(
            "[ivr_webhook] HELENA_PUBLIC_WEBHOOK_URL definida pero falta HELENA_WEBHOOK_SECRET: "
            "no se registra el webhook (los eventos entrantes se rechazarían por firma)"
        )
        return

    try:
        client = HelenaClient(load_helena_config())
        existing = await _find_existing(client, public_url)

        payload: dict[str, Any] = {
            "url": public_url,
            "events": list(SUBSCRIBED_EVENTS),
            "secret": secret,
            "description": _DESCRIPTION,
        }

        if existing is None:
            created = await client.register_webhook(payload)
            logger.info(
                "[ivr_webhook] webhook registrado en Helena | id=%s url=%s",
                _extract(created, "id"),
                public_url,
            )
            return

        webhook_id = _extract(existing, "id")
        await client.update_webhook(str(webhook_id), payload)
        logger.info(
            "[ivr_webhook] webhook ya existía, actualizado | id=%s url=%s",
            webhook_id,
            public_url,
        )

    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "[ivr_webhook] no se pudo registrar el webhook en Helena (se continúa): %s", exc
        )


async def _find_existing(client: HelenaClient, url: str) -> dict[str, Any] | None:
    body = await client.list_webhooks()
    for item in _as_list(body):
        if isinstance(item, dict) and str(item.get("url", "")).strip() == url:
            return item
    return None


def _as_list(body: Any) -> list[Any]:
    """Normaliza la respuesta: Helena puede devolver la lista cruda o envuelta."""
    if isinstance(body, list):
        return body
    if isinstance(body, dict):
        for key in ("data", "webhooks", "items"):
            value = body.get(key)
            if isinstance(value, list):
                return value
    return []


def _extract(body: Any, key: str) -> Any:
    if isinstance(body, dict):
        if key in body:
            return body[key]
        data = body.get("data")
        if isinstance(data, dict):
            return data.get(key)
    return None
