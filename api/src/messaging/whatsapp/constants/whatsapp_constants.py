# Confirmado contra https://developers.facebook.com/documentation/business-messaging/whatsapp/templates/overview
# (ejemplo de creación de plantillas usa v23.0).
GRAPH_API_VERSION = "v23.0"
GRAPH_API_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

MESSAGES_ENDPOINT = "/{phone_number_id}/messages"
MESSAGE_TEMPLATES_ENDPOINT = "/{waba_id}/message_templates"
TEMPLATE_BY_ID_ENDPOINT = "/{template_id}"
