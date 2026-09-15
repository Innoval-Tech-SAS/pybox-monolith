from typing import Any

import httpx

from core.config.logger import logger
from core.tools.config_tools import get_or_throw
from messaging.whatsapp.constants.whatsapp_constants import (
    GRAPH_API_BASE_URL,
    MESSAGE_TEMPLATES_ENDPOINT,
    MESSAGES_ENDPOINT,
    TEMPLATE_BY_ID_ENDPOINT,
)


class WhatsAppCloudClient:
    """Cliente HTTP a la Graph API de Meta (WhatsApp Cloud API).

    Token, app_secret y waba_id son de la app/WABA (una sola, compartida entre
    organizaciones) y se cargan una sola vez. `phone_number_id` en cambio es por
    organización y se recibe como parámetro en cada llamada de envío.
    """

    def __new__(cls) -> "WhatsAppCloudClient":
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._token = get_or_throw("WHATSAPP_CLOUD_ACCESS_TOKEN")
            cls._instance._waba_id = get_or_throw("WHATSAPP_CLOUD_WABA_ID")
            # Un solo cliente reutilizado entre llamadas: abrir/cerrar conexión TLS
            # por request se vuelve el cuello de botella dominante en un envío masivo.
            cls._instance._http = httpx.AsyncClient(timeout=15)
        return cls._instance

    async def _request(
        self,
        method: str,
        endpoint: str,
        json: dict | None = None,
        params: dict | None = None,
        token: str | None = None,
    ) -> httpx.Response:
        headers = {"Authorization": f"Bearer {token or self._token}"}
        response = await self._http.request(
            method, f"{GRAPH_API_BASE_URL}{endpoint}", json=json, params=params, headers=headers
        )
        response.raise_for_status()
        return response

    async def send_template(
        self,
        phone_number_id: str,
        to: str,
        template_name: str,
        language: str,
        components: list[dict[str, Any]],
        token: str | None = None,
    ) -> tuple[bool, str | None]:
        endpoint = MESSAGES_ENDPOINT.format(phone_number_id=phone_number_id)
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
                "components": components,
            },
        }
        try:
            response = await self._request("POST", endpoint, json=payload, token=token)
            body = response.json()
            messages = body.get("messages", [])
            wamid = messages[0]["id"] if messages else None
            logger.info("[whatsapp] send_ok | to=%s template=%s wamid=%s", to, template_name, wamid)
            return True, wamid
        except httpx.HTTPStatusError as exc:
            response_body = exc.response.text[:500] if exc.response is not None else ""
            logger.error(
                "[whatsapp] send_http_error | status=%s body=%s",
                exc.response.status_code if exc.response is not None else "?",
                response_body,
            )
            return False, None
        except Exception as exc:
            logger.error("[whatsapp] send_error | error=%s detail=%s", type(exc).__name__, exc)
            return False, None

    async def send_text(
        self,
        phone_number_id: str,
        to: str,
        body: str,
        token: str | None = None,
    ) -> tuple[bool, str | None]:
        """Mensaje de texto libre (fuera de plantilla) — solo válido dentro de la
        ventana de servicio al cliente de 24h desde el último mensaje del deudor."""
        endpoint = MESSAGES_ENDPOINT.format(phone_number_id=phone_number_id)
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"body": body},
        }
        try:
            response = await self._request("POST", endpoint, json=payload, token=token)
            body_json = response.json()
            messages = body_json.get("messages", [])
            wamid = messages[0]["id"] if messages else None
            logger.info("[whatsapp] send_text_ok | to=%s wamid=%s", to, wamid)
            return True, wamid
        except httpx.HTTPStatusError as exc:
            response_body = exc.response.text[:500] if exc.response is not None else ""
            logger.error(
                "[whatsapp] send_text_http_error | status=%s body=%s",
                exc.response.status_code if exc.response is not None else "?",
                response_body,
            )
            return False, None
        except Exception as exc:
            logger.error("[whatsapp] send_text_error | error=%s detail=%s", type(exc).__name__, exc)
            return False, None

    async def create_template(
        self,
        name: str,
        category: str,
        language: str,
        components: list[dict[str, Any]],
    ) -> dict[str, Any]:
        endpoint = MESSAGE_TEMPLATES_ENDPOINT.format(waba_id=self._waba_id)
        # Explícito: todo el resto del código (parser de variables, armado de
        # components al enviar) asume {{nombre}} nombrado, no {{1}} posicional — así
        # las variables se resuelven por nombre contra columnas de deudores/creditos
        # en ejecución (igual que SMS/Email), sin depender de mapear posiciones.
        payload = {
            "name": name,
            # Los ejemplos confirmados de creación (utility-templates) usan minúscula
            # en el REQUEST ("category": "utility"), aunque la respuesta y el listado
            # de plantillas la devuelven en mayúscula ("UTILITY") — se normaliza acá,
            # el enum interno (`WhatsAppTemplateCategory`) se queda en mayúscula.
            "category": category.lower(),
            "language": language,
            "parameter_format": "NAMED",
            "components": components,
        }
        response = await self._request("POST", endpoint, json=payload)
        return response.json()

    async def get_template(self, meta_template_id: str) -> dict[str, Any]:
        endpoint = TEMPLATE_BY_ID_ENDPOINT.format(template_id=meta_template_id)
        response = await self._request("GET", endpoint)
        return response.json()

    async def delete_template(self, name: str) -> None:
        endpoint = MESSAGE_TEMPLATES_ENDPOINT.format(waba_id=self._waba_id)
        await self._request("DELETE", endpoint, params={"name": name})
