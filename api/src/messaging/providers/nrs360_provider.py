import httpx
from config.logger import logger
from tools.config_tools import get_or_throw


class NRS360Provider:
    _SMS_URL = "https://dashboard.360nrs.com/api/rest/sms"
    _EMAIL_URL = "https://dashboard.360nrs.com/api/rest/mailing"

    def __init__(self) -> None:
        self._sms_token = get_or_throw("NRS360_SMS_TOKEN")
        self._email_token = get_or_throw("NRS360_EMAIL_TOKEN")

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
        headers = {"Authorization": self._sms_token}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(self._SMS_URL, json=payload, headers=headers)
            response.raise_for_status()
            logger.info("[nrs360] sms_sent | recipients=%d", len(to))
            return True
        except Exception as exc:
            logger.error("[nrs360] sms_error | error=%s", type(exc).__name__)
            return False

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
            "fromName": "Template App",
            "campaignName": "otp-verification",
        }
        if sub:
            payload["sub"] = sub
        headers = {"Authorization": self._email_token}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(self._EMAIL_URL, json=payload, headers=headers)
            response.raise_for_status()
            logger.info("[nrs360] email_sent | recipients=%d", len(to))
            return True
        except Exception as exc:
            logger.error("[nrs360] email_error | error=%s", type(exc).__name__)
            return False
