from typing import Any

from messaging.providers.nrs360_provider import NRS360Provider


class SmsChannel:
    def __init__(self, provider: NRS360Provider) -> None:
        self._provider = provider

    async def send(self, to: list[str], message: str, **kwargs: Any) -> bool:
        sender: str = kwargs.get("sender", "Template")
        sub: list[dict] | None = kwargs.get("sub")
        return await self._provider.send_sms(message=message, to=to, sender=sender, sub=sub)
