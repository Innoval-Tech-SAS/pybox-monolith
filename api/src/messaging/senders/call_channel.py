from typing import Any


class CallChannel:
    sends_per_recipient = True

    async def send(self, to: list[str], message: str, **kwargs: Any) -> bool:
        raise NotImplementedError("Call provider not configured")
