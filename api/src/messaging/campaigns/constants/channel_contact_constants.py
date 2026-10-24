"""Mapeo de canal de envío al tipo de método de contacto que necesita."""

from messaging.channels.enums.channel_enums import ChannelName
from receivables.contact_methods.enums.contact_method_enums import ContactMethodType

# Canal de envío → tipo de contacto que se resuelve desde ``metodos_contacto``.
CHANNEL_CONTACT_TYPE: dict[ChannelName, ContactMethodType] = {
    ChannelName.SMS: ContactMethodType.PHONE,
    ChannelName.WHATSAPP: ContactMethodType.PHONE,
    ChannelName.CALL: ContactMethodType.PHONE,
    ChannelName.CALL_IA: ContactMethodType.PHONE,
    ChannelName.EMAIL: ContactMethodType.EMAIL,
}
