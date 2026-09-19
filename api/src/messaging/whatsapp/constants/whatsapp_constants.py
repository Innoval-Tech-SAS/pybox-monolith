# Confirmado contra https://developers.facebook.com/documentation/business-messaging/whatsapp/templates/overview
# (ejemplo de creación de plantillas usa v23.0).
GRAPH_API_VERSION = "v23.0"
GRAPH_API_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

MESSAGES_ENDPOINT = "/{phone_number_id}/messages"
MESSAGE_TEMPLATES_ENDPOINT = "/{waba_id}/message_templates"
TEMPLATE_BY_ID_ENDPOINT = "/{template_id}"

# Códigos de error de la Graph API (https://developers.facebook.com/docs/graph-api/guides/error-handling)
META_AUTH_ERROR_CODES = frozenset({190})
META_PERMISSION_ERROR_CODES = frozenset({10, *range(200, 300)})
META_RATE_LIMIT_ERROR_CODES = frozenset({4, 17, 32, 613, 80007})
META_ERROR_DETAIL_MAX_CHARS = 300

META_ERROR_AUTH_MESSAGE = (
    "La conexión de la plataforma con WhatsApp (Meta) no está autorizada: el token de acceso "
    "es inválido o expiró. Contacta al administrador de la plataforma."
)
META_ERROR_PERMISSION_MESSAGE = (
    "Meta rechazó la operación: la cuenta de WhatsApp Business de la plataforma no tiene permisos "
    "para gestionar plantillas. Contacta al administrador de la plataforma."
)
META_ERROR_RATE_LIMIT_MESSAGE = "Meta limitó temporalmente las solicitudes. Espera unos minutos e inténtalo de nuevo."
META_ERROR_UNAVAILABLE_MESSAGE = "Meta no está disponible en este momento. Inténtalo de nuevo en unos minutos."
META_ERROR_UNREACHABLE_MESSAGE = "No fue posible comunicarse con Meta. Inténtalo de nuevo en unos minutos."
META_ERROR_REJECTED_MESSAGE = "Meta rechazó la solicitud: {detail}"
META_ERROR_REJECTED_NO_DETAIL_MESSAGE = "Meta rechazó la solicitud sin indicar el motivo."
