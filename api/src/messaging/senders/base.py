from typing import Any, Protocol


class ChannelSender(Protocol):
    sends_per_recipient: bool
    async def send(self, to: list[str], message: str, **kwargs: Any) -> bool: ...
