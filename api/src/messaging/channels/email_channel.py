from typing import Any

from messaging.providers.nrs360_provider import NRS360Provider


class EmailChannel:
    def __init__(self, provider: NRS360Provider) -> None:
        self._provider = provider

    async def send(self, to: list[str], message: str, **kwargs: Any) -> bool:
        subject: str = kwargs.get("subject", "")
        sub: list[dict] | None = kwargs.get("sub")
        return await self._provider.send_email(subject=subject, body=message, to=to, sub=sub)
