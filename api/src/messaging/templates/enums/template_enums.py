"""Canal y estado de una plantilla de mensajería."""

from enum import StrEnum

from messaging.channels.enums.channel_enums import ChannelName

TemplateChannel = ChannelName


class TemplateStatus(StrEnum):
    DRAFT = "BORRADOR"
    ACTIVE = "ACTIVA"
    INACTIVE = "INACTIVA"
