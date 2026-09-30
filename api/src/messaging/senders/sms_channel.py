"""Adaptador de canal SMS: traduce la interfaz común de envío al provider 360NRS."""

from typing import Any

from messaging.providers.sms_provider import NRS360SmsProvider


class SmsChannel:
    sends_per_recipient = False

    def __init__(self, provider: NRS360SmsProvider) -> None:
        self._provider = provider

    async def send(
        self, to: list[str], message: str, **kwargs: Any
    ) -> tuple[bool, dict[str, str] | None, str | None]:
        sub: list[dict] | None = kwargs.get("sub")
        credential = kwargs.get("credential")
        return await self._provider.send_sms(
            message=message,
            to=to,
            sub=sub,
            campaign_name=kwargs.get("campaign_name"),
            token=credential.get("token") if credential else None,
            sender=credential.get("sender") if credential else None,
        )
