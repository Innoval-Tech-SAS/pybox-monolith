from core.config.logger import logger
from core.tools.config_tools import get_or_throw
from messaging.constants.nrs360_constants import SMS_URL
from messaging.providers.base_provider import NRS360BaseProvider


class NRS360SmsProvider(NRS360BaseProvider):

    def __new__(cls) -> "NRS360SmsProvider":
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._token = get_or_throw("NRS360_SMS_TOKEN")
        return cls._instance

    async def send_sms(
        self,
        message: str,
        to: list[str],
        sender: str,
        sub: list[dict] | None = None,
    ) -> bool:
        payload: dict = {
            "message": message,
            "to": to,
            "sender": sender,
            "campaignName": "otp-verification",
        }
        if sub:
            payload["sub"] = sub
        try:
            await self._request("POST", SMS_URL, self._token, json=payload)
            logger.info("[nrs360] sms_sent | recipients=%d", len(to))
            return True
        except Exception as exc:
            logger.error("[nrs360] sms_error | error=%s", type(exc).__name__)
            return False
