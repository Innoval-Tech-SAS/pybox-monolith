from typing import Any

from messaging.providers.email_provider import NRS360EmailProvider


class EmailChannel:
    sends_per_recipient = True

    def __init__(self, provider: NRS360EmailProvider) -> None:
        self._provider = provider

    async def send(self, to: list[str], message: str, **kwargs: Any) -> tuple[bool, dict[str, str] | None, str | None]:
        subject: str = kwargs.get("subject", "")
        sub: list[dict] | None = kwargs.get("sub")
        return await self._provider.send_email(subject=subject, body=message, to=to, sub=sub)
