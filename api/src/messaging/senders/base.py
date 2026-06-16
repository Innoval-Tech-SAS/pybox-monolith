from typing import Any, Protocol


class ChannelSender(Protocol):
    async def send(self, to: list[str], message: str, **kwargs: Any) -> bool: ...
