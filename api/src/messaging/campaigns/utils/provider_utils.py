import re

from messaging.campaigns.constants import NRS360_CHANNELS
from messaging.channels.enums.channel_enums import ChannelName
from messaging.contacts.enums.contact_enums import ProviderType

_PHONE_CHANNELS = frozenset(
    {ChannelName.SMS, ChannelName.WHATSAPP, ChannelName.CALL, ChannelName.CALL_IA}
)


def provider_for_channel(channel_name: str) -> ProviderType | None:
    if channel_name in NRS360_CHANNELS:
        return ProviderType.NRS360
    if channel_name == ChannelName.WHATSAPP:
        return ProviderType.WHATSAPP_CLOUD
    if channel_name == ChannelName.CALL:
        return ProviderType.HELENA
    return None


def is_phone_channel(channel_name: str) -> bool:
    return channel_name in _PHONE_CHANNELS


def normalize_phone(value: str, country_code: str) -> str:
    """Antepone el indicativo de país (solo dígitos) al número si no lo trae ya.

    Deja solo dígitos en ambos (quita ``+``, espacios, guiones). Un número local se
    devuelve como ``{indicativo}{numero}``; si ya venía con el indicativo se respeta.
    """
    digits = re.sub(r"\D", "", value or "")
    code = re.sub(r"\D", "", country_code or "")
    if not digits or not code:
        return value
    # Un número local de la región tiene ≤10 dígitos; si ya trae más y arranca con el
    # indicativo, se asume normalizado y no se vuelve a prefijar.
    if digits.startswith(code) and len(digits) > 10:
        return digits
    return f"{code}{digits}"
