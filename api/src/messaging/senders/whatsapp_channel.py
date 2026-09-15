from typing import Any

from messaging.whatsapp.services.whatsapp_client import WhatsAppCloudClient


def _build_components(variables: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not variables:
        return []
    # Las claves del `sub` son los nombres reales de columna (ej. "nombre_completo",
    # "saldo_total") — igual convención que SMS/Email, resueltas por nombre contra
    # {{nombre}} del body aprobado en Meta. El orden no importa en params nombrados.
    parameters = [
        {"type": "text", "parameter_name": key, "text": str(value)}
        for key, value in variables.items()
    ]
    return [{"type": "body", "parameters": parameters}]


class WhatsAppChannel:
    sends_per_recipient = True

    def __init__(self, client: WhatsAppCloudClient) -> None:
        self._client = client

    async def send(self, to: list[str], message: str, **kwargs: Any) -> tuple[bool, dict[str, str] | None, str | None]:
        phone_number_id: str | None = kwargs.get("phone_number_id")
        language: str | None = kwargs.get("language")
        if not phone_number_id or not language:
            raise ValueError("WhatsApp requiere 'phone_number_id' y 'language' para enviar")

        sub: list[dict] | None = kwargs.get("sub")
        variables = sub[0] if sub else None
        components = _build_components(variables)

        credential = kwargs.get("credential")
        recipient = to[0]
        ok, wamid = await self._client.send_template(
            phone_number_id=phone_number_id,
            to=recipient,
            template_name=message,
            language=language,
            components=components,
            token=credential.get("access_token") if credential else None,
        )
        ids_by_recipient = {recipient: wamid} if ok and wamid else None
        return ok, ids_by_recipient, None
