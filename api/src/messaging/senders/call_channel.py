from typing import Any

from messaging.ivr.providers.helena_call_provider import HelenaCallProvider


class CallChannel:
    """Canal de llamadas IVR (Helena). Envía un único bulk por lote.

    El motor de campañas entrega la lista de destinatarios (`targets`) y el
    contexto IVR (`ivr_context`: ivr_config + redial_config + campaign_id) vía
    kwargs desde el `BatchSender`.
    """

    sends_per_recipient = False

    def __init__(self, provider: HelenaCallProvider) -> None:
        self._provider = provider

    async def send(
        self, to: list[str], message: str, **kwargs: Any
    ) -> tuple[bool, dict[str, str] | None, str | None]:
        ivr_context: dict[str, Any] | None = kwargs.get("ivr_context")
        targets: list[dict[str, Any]] | None = kwargs.get("targets")

        if not ivr_context or not ivr_context.get("ivr_config"):
            raise ValueError("Campaña IVR sin ivr_config: se requiere un flujo IVR configurado")

        # Fallback: si no llegan targets estructurados, arma phones desde `to`.
        if not targets:
            targets = [{"phone": phone} for phone in to]

        return await self._provider.send_bulk(
            targets=targets,
            ivr_config=ivr_context["ivr_config"],
            campaign_id=str(ivr_context.get("campaign_id") or ""),
            redial_config=ivr_context.get("redial_config"),
            caller_id=ivr_context.get("caller_id"),
            default_variables=ivr_context.get("variables"),
            ivr_flow_id=ivr_context.get("ivr_flow_id"),
            calls_per_second=ivr_context.get("calls_per_second"),
            max_concurrent=ivr_context.get("max_concurrent"),
            contact_policy_id=ivr_context.get("contact_policy_id"),
        )
