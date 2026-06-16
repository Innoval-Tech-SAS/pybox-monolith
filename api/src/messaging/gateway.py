from typing import Any

from messaging.channels.call_channel import CallChannel
from messaging.channels.email_channel import EmailChannel
from messaging.channels.sms_channel import SmsChannel
from messaging.channels.whatsapp_channel import WhatsAppChannel
from messaging.constants import channels
from messaging.providers.nrs360_provider import NRS360Provider


class DeliveryGateway:
    def __init__(self) -> None:
        nrs = NRS360Provider()
        self._channels = {
            channels.SMS: SmsChannel(nrs),
            channels.EMAIL: EmailChannel(nrs),
            channels.WHATSAPP: WhatsAppChannel(),
            channels.CALL: CallChannel(),
        }

    async def send(self, channel: str, to: list[str], message: str, **kwargs: Any) -> bool:
        sender = self._channels.get(channel)
        if sender is None:
            raise ValueError(f"Canal no soportado: {channel}")
        return await sender.send(to, message, **kwargs)
