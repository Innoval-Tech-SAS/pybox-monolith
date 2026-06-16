from enum import Enum

from messaging.channels.enums.channel_enums import ChannelName


TemplateChannel = ChannelName


class TemplateStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
