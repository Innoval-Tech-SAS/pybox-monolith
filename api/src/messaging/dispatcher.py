from typing import Any

from messaging.senders.base import ChannelSender
from messaging.senders.call_channel import CallChannel
from messaging.senders.call_ia_channel import CallIaChannel
from messaging.senders.email_channel import EmailChannel
from messaging.senders.sms_channel import SmsChannel
from messaging.senders.whatsapp_channel import WhatsAppChannel
from messaging.channels.enums.channel_enums import ChannelName
from messaging.providers.email_provider import NRS360EmailProvider
from messaging.providers.sms_provider import NRS360SmsProvider


class MessageDispatcher:
    def __init__(self) -> None:
        self._channels: dict[str, ChannelSender] = {
            ChannelName.SMS: SmsChannel(NRS360SmsProvider()),
            ChannelName.EMAIL: EmailChannel(NRS360EmailProvider()),
            ChannelName.WHATSAPP: WhatsAppChannel(),
            ChannelName.CALL: CallChannel(),
            ChannelName.CALL_IA: CallIaChannel(),
        }

    def get_sender(self, channel: str) -> ChannelSender:
        sender = self._channels.get(channel)
        if sender is None:
            raise ValueError(f"Canal no soportado: {channel}")
        return sender

    async def send(self, channel: str, to: list[str], message: str, **kwargs: Any) -> tuple[bool, dict[str, str] | None, str | None]:
        return await self.get_sender(channel).send(to, message, **kwargs)
