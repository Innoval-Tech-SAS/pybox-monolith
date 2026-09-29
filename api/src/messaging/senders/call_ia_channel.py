from typing import Any


class CallIaChannel:
    sends_per_recipient = True

    async def send(
        self, to: list[str], message: str, **kwargs: Any
    ) -> tuple[bool, dict[str, str] | None, str | None]:
        raise NotImplementedError("Call IA provider not configured")
