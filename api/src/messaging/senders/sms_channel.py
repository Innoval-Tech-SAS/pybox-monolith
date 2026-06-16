from typing import Any

from messaging.providers.sms_provider import NRS360SmsProvider


class SmsChannel:
    sends_per_recipient = False

    def __init__(self, provider: NRS360SmsProvider) -> None:
        self._provider = provider

    async def send(self, to: list[str], message: str, **kwargs: Any) -> tuple[bool, dict[str, str] | None, str | None]:
        sender: str = kwargs.get("sender", "Template")
        sub: list[dict] | None = kwargs.get("sub")
        return await self._provider.send_sms(message=message, to=to, sender=sender, sub=sub)
