from core.config.logger import logger
from core.tools.config_tools import get_or_throw
from messaging.constants.nrs360_constants import EMAIL_URL
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
    ) -> bool:
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
        try:
            await self._request("POST", EMAIL_URL, self._token, json=payload)
            logger.info("[nrs360] email_sent | recipients=%d", len(to))
            return True
        except Exception as exc:
            logger.error("[nrs360] email_error | error=%s", type(exc).__name__)
            return False
