from typing import Any


class WhatsAppChannel:
    sends_per_recipient = True

    async def send(self, to: list[str], message: str, **kwargs: Any) -> bool:
        raise NotImplementedError("WhatsApp provider not configured")
