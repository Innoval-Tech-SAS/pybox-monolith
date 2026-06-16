from typing import Any


class WhatsAppChannel:
    async def send(self, to: list[str], message: str, **kwargs: Any) -> bool:
        raise NotImplementedError("WhatsApp provider not configured")
