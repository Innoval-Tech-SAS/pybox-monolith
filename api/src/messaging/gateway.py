from typing import Any

from messaging.senders.base import ChannelSender
from messaging.senders.call_channel import CallChannel
from messaging.senders.email_channel import EmailChannel
from messaging.senders.sms_channel import SmsChannel
from messaging.senders.whatsapp_channel import WhatsAppChannel
from messaging.constants import channels
from messaging.providers.nrs360_provider import NRS360Provider


class DeliveryGateway:
    def __init__(self) -> None:
        nrs = NRS360Provider()
        self._channels: dict[str, ChannelSender] = {
            channels.SMS: SmsChannel(nrs),
            channels.EMAIL: EmailChannel(nrs),
            channels.WHATSAPP: WhatsAppChannel(),
            channels.CALL: CallChannel(),
        }

    def get_sender(self, channel: str) -> ChannelSender:
        sender = self._channels.get(channel)
        if sender is None:
            raise ValueError(f"Canal no soportado: {channel}")
        return sender

    async def send(self, channel: str, to: list[str], message: str, **kwargs: Any) -> bool:
        return await self.get_sender(channel).send(to, message, **kwargs)
