from typing import Any


class CallChannel:
    async def send(self, to: list[str], message: str, **kwargs: Any) -> bool:
        raise NotImplementedError("Call provider not configured")
