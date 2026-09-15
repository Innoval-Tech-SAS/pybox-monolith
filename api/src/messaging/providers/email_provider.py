import httpx

from core.config.logger import logger
from core.tools.config_tools import get_or_throw
from messaging.constants.nrs360_constants import EMAIL_ENDPOINT
from messaging.providers.base_provider import NRS360BaseProvider


class NRS360EmailProvider(NRS360BaseProvider):

    def __new__(cls) -> "NRS360EmailProvider":
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._token = get_or_throw("NRS360_EMAIL_TOKEN")
            cls._instance._sender = get_or_throw("NRS360_EMAIL_SENDER")
            cls._instance._sender_name = get_or_throw("NRS360_EMAIL_SENDER_NAME")
            cls._instance._http = httpx.AsyncClient(timeout=cls._TIMEOUT_SECONDS)
        return cls._instance

    async def send_email(
        self,
        subject: str,
        body: str,
        to: list[str],
        sub: list[dict] | None = None,
        campaign_name: str | None = None,
        token: str | None = None,
        sender: str | None = None,
        sender_name: str | None = None,
    ) -> tuple[bool, dict[str, str] | None, str | None]:
        # Credenciales por país (DB) si se pasan; si no, fallback al entorno.
        token = token or self._token
        sender = sender or self._sender
        sender_name = sender_name or self._sender_name
        payload: dict = {
            "subject": subject,
            "body": body,
            "to": to,
            "fromEmail": sender,
            "fromName": sender_name,
            "replyTo": sender,
            "campaignName": campaign_name or "otp-verification",
        }
        if sub:
            payload["sub"] = sub
        logger.info("[nrs360] email_send_start | recipients=%d", len(to))
        try:
            response = await self._request("POST", EMAIL_ENDPOINT, token, json=payload)
            body_json = response.json()
            result = body_json.get("result", [])
            ids_by_recipient = {item["to"]: item["id"] for item in result if item.get("id")}
            sending_id = body_json.get("sendingId")
            logger.info(
                "[nrs360] email_sent | recipients=%d response_items=%d sending_id=%s",
                len(to),
                len(result),
                sending_id,
            )
            return True, ids_by_recipient, str(sending_id) if sending_id is not None else None
        except httpx.HTTPStatusError as exc:
            response_body = exc.response.text[:500] if exc.response is not None else ""
            logger.error(
                "[nrs360] email_http_error | status=%s body=%s",
                exc.response.status_code if exc.response is not None else "?",
                response_body,
            )
            return False, None, None
        except Exception as exc:
            logger.error("[nrs360] email_error | error=%s detail=%s", type(exc).__name__, exc)
            return False, None, None
