import httpx
from config.logger import logger
from tools.config_tools import get_or_throw


class NRS360Provider:
    _SMS_URL = "https://dashboard.360nrs.com/api/rest/sms"
    _EMAIL_URL = "https://dashboard.360nrs.com/api/rest/mailing"

    def __init__(self) -> None:
        self._sms_token = get_or_throw("NRS360_SMS_TOKEN")
        self._email_token = get_or_throw("NRS360_EMAIL_TOKEN")

    async def send_sms(self, message: str, to: list[str], sender: str) -> bool:
        payload = {
            "message": message,
            "to": to,
            "sender": sender,
            "campaignName": "otp-verification",
        }
        headers = {"Authorization": f"Basic {self._sms_token}"}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(self._SMS_URL, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"SMS enviado a {to} vía 360NRS")
            return True
        except Exception as exc:
            logger.error(f"Error al enviar SMS por 360NRS: {exc}")
            return False

    async def send_email(self, subject: str, body: str, to: list[str]) -> bool:
        payload = {
            "subject": subject,
            "body": body,
            "to": to,
            "from": "info@puntualmente.info",
            "fromName": "Template App",
            "campaignName": "otp-verification",
        }
        headers = {"Authorization": f"Basic {self._email_token}"}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(self._EMAIL_URL, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"Email enviado a {to} vía 360NRS")
            return True
        except Exception as exc:
            logger.error(f"Error al enviar email por 360NRS: {exc}")
            return False
