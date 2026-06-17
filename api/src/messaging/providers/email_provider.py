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
        return cls._instance

    async def send_email(
        self,
        subject: str,
        body: str,
        to: list[str],
        sub: list[dict] | None = None,
    ) -> tuple[bool, dict[str, str] | None, str | None]:
        payload: dict = {
            "subject": subject,
            "body": body,
            "to": to,
            "from": "info@puntualmente.info",
            "fromName": "PYBOX Info",
            "campaignName": "otp-verification",
        }
        if sub:
            payload["sub"] = sub
        logger.info("[nrs360] email_send_start | recipients=%d", len(to))
        try:
            response = await self._request("POST", EMAIL_ENDPOINT, self._token, json=payload)
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
