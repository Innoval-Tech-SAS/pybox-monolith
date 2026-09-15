from enum import StrEnum


class WhatsAppTemplateCategory(StrEnum):
    # Categorías definidas por Meta/WhatsApp (tercero) — se mantienen en inglés.
    MARKETING = "MARKETING"
    UTILITY = "UTILITY"
    AUTHENTICATION = "AUTHENTICATION"


class ChannelRequestStatus(StrEnum):
    PENDING = "PENDIENTE"
    APPROVED = "APROBADA"
    REJECTED = "RECHAZADA"


class MessageDirection(StrEnum):
    INBOUND = "ENTRANTE"
    OUTBOUND = "SALIENTE"


class WhatsAppMessageType(StrEnum):
    """Tipo de un mensaje de WhatsApp — espejo literal del campo `type` que documenta
    la API de Meta (Cloud API), no se traduce (mismo criterio que WhatsAppTemplateCategory).

    Confirmado con la documentación oficial de Meta for Developers:
    - Entrante (webhook `messages[].type`): TEXT/IMAGE/AUDIO/VIDEO/DOCUMENT/STICKER/
      LOCATION/CONTACTS/INTERACTIVE/REACTION/BUTTON/ORDER/SYSTEM, más UNKNOWN cuando
      Meta manda un tipo que la Cloud API no soporta.
    - Saliente (`POST /messages`): TEXT/TEMPLATE/IMAGE/DOCUMENT/AUDIO/VIDEO/STICKER/
      LOCATION/CONTACTS/INTERACTIVE/REACTION.
    Este enum es la unión de ambos conjuntos.
    """

    TEXT = "text"
    TEMPLATE = "template"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    STICKER = "sticker"
    LOCATION = "location"
    CONTACTS = "contacts"
    INTERACTIVE = "interactive"
    REACTION = "reaction"
    BUTTON = "button"
    ORDER = "order"
    SYSTEM = "system"
    UNKNOWN = "unknown"
