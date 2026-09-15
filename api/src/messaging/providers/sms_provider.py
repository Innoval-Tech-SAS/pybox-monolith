import httpx

from core.config.logger import logger
from core.tools.config_tools import get_or_throw
from messaging.constants.nrs360_constants import SMS_ENDPOINT, SMS_MAX_PARTS
from messaging.providers.base_provider import NRS360BaseProvider
from messaging.utils.sms_encoding_utils import resolve_sms_encoding, resolve_sms_parts


def _sub_shape(sub: list[dict] | None) -> str:
    """Describe la estructura del ``sub`` (solo claves, sin valores) para diagnóstico.

    No expone valores: en producción el ``sub`` lleva el código OTP o datos personales
    del deudor. La forma basta para detectar formatos inválidos (p. ej. el envoltorio
    ``{"values": {...}}`` que 360nrs no espera, o dicts vacíos ``{}``).
    """
    if not sub:
        return "none"

    def keys(d: dict) -> str:
        parts: list[str] = []
        for key, value in d.items():
            if isinstance(value, dict):
                parts.append(f"{key}:{{{keys(value)}}}")
            else:
                parts.append(str(key))
        return ",".join(parts)

    elements = ["{" + keys(el) + "}" if isinstance(el, dict) else type(el).__name__ for el in sub]
    return "[" + "; ".join(elements) + "]"


class NRS360SmsProvider(NRS360BaseProvider):

    def __new__(cls) -> "NRS360SmsProvider":
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._token = get_or_throw("NRS360_SMS_TOKEN")
            cls._instance._sender = get_or_throw("NRS360_SMS_SENDER")
            cls._instance._http = httpx.AsyncClient(timeout=cls._TIMEOUT_SECONDS)
        return cls._instance

    async def send_sms(
        self,
        message: str,
        to: list[str],
        sub: list[dict] | None = None,
        campaign_name: str | None = None,
        token: str | None = None,
        sender: str | None = None,
    ) -> tuple[bool, dict[str, str] | None, str | None]:
        # Credenciales por país (descifradas de DB) si el call site las pasa; si no,
        # se cae al token/sender del entorno (comportamiento previo) — así el rewire
        # nunca rompe un envío por falta de credencial en DB.
        token = token or self._token
        sender = sender or self._sender
        encoding = resolve_sms_encoding(message, sub)
        # ``parts`` va explícito: su default es 1 y un mensaje que necesite más partes de
        # las declaradas no se trunca, falla con error 105. Al elegir ``utf-16`` la parte
        # baja de 160 a 70 caracteres, así que omitirlo rompería justo los mensajes con
        # acentos que este encoding pretende arreglar.
        parts = resolve_sms_parts(message, sub, encoding)
        if parts >= SMS_MAX_PARTS:
            logger.warning(
                "[nrs360] sms_parts_capped | encoding=%s parts=%d campaign=%s",
                encoding,
                parts,
                campaign_name,
            )
        payload: dict = {
            "message": message,
            "to": to,
            "from": sender,
            "campaignName": campaign_name or "otp-verification",
            "encoding": encoding,
            "parts": parts,
        }
        if sub:
            payload["sub"] = sub
        logger.info("[nrs360] sms_send_start | recipients=%d", len(to))
        # Payload de salida (sin valores del sub) para poder contrastar el envío OTP contra
        # el de campaña ante el error 360nrs code=101 "Internal Database error".
        logger.info(
            "[nrs360] sms_payload | to=%d from=%s campaign=%s encoding=%s parts=%d sub_len=%d sub_shape=%s",
            len(to),
            sender,
            payload["campaignName"],
            encoding,
            parts,
            len(sub) if sub else 0,
            _sub_shape(sub),
        )
        try:
            response = await self._request("POST", SMS_ENDPOINT, token, json=payload)
            body = response.json()
            result = body.get("result", [])
            ids_by_recipient = {item["to"]: item["id"] for item in result if item.get("id")}
            sending_id = body.get("sendingId")
            logger.info(
                "[nrs360] sms_sent | recipients=%d response_items=%d sending_id=%s",
                len(to),
                len(result),
                sending_id,
            )
            return True, ids_by_recipient, str(sending_id) if sending_id is not None else None
        except httpx.HTTPStatusError as exc:
            response_body = exc.response.text[:500] if exc.response is not None else ""
            logger.error(
                "[nrs360] sms_http_error | status=%s body=%s",
                exc.response.status_code if exc.response is not None else "?",
                response_body,
            )
            return False, None, None
        except Exception as exc:
            logger.error("[nrs360] sms_error | error=%s detail=%s", type(exc).__name__, exc)
            return False, None, None
