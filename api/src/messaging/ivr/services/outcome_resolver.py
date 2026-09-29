"""Traducción del resultado técnico de una llamada a un resultado de negocio.

Helena reporta *dónde* y *por qué* terminó una llamada (`ivrEndNodeId` +
`ivrEndReason`). Eso no le sirve a un gestor de cartera: "colgó en `menu_1` por
`CUSTOMER_HANGUP`" tiene que poder leerse como "no quiso atender".

El diseñador de flujos define una etiqueta libre por cada desenlace posible, y
ese mapa se guarda compilado en `flujos_ivr.outcomes`:

    {
      "__call_level__": {"no_answer": "No contestó", "voicemail": "Buzón", ...},
      "menu_1":         {"OPTION": "Aceptó acuerdo", "abandono": "Colgó en el menú"},
      ...
    }

Portado de `collect_send_masivos/src/services/helena/webhook_processor.py`
(`_resolve_outcome`), adaptado: allí la clave resolvía a un código de gestión
del CRM legacy; aquí resuelve a una etiqueta de texto (decisión de la fase 6).
"""

from __future__ import annotations

from typing import Any

#: Nodo virtual para las llamadas que nunca entraron al IVR (no hay
#: `ivrEndNodeId` que consultar).
CALL_LEVEL_NODE = "__call_level__"

#: Razones que Helena genera por su cuenta, no configuradas por el diseñador.
SYSTEM_REASON_TO_KEY: dict[str, str] = {
    "CUSTOMER_HANGUP": "abandono",
    "TRANSFER_AGENT_HANGUP": "answered",
    "MAX_RETRIES_EXCEEDED": "max_retries_exceeded",
}

#: Claves del nodo virtual de nivel de llamada.
CALL_LEVEL_KEYS: tuple[str, ...] = (
    "no_answer",
    "voicemail",
    "abandono",
    "out_of_schedule",
    "cancelled",
)


def resolve_outcome(
    *,
    ivr_end_node_id: str | None,
    ivr_end_reason: str | None,
    dial_status: str | None,
    amd_status: str | None,
    outcomes: dict[str, Any] | None,
) -> tuple[str, str | None]:
    """Devuelve `(clave, etiqueta)` del resultado de negocio de una llamada.

    La clave siempre se puede calcular; la etiqueta es `None` si el flujo no
    tiene configurado ese desenlace (no es un error: la llamada igual se cierra).
    """
    node_name, key = _resolve_key(
        ivr_end_node_id, ivr_end_reason, dial_status, amd_status
    )

    node_outcomes = (outcomes or {}).get(node_name)
    if not isinstance(node_outcomes, dict):
        return key, None

    label = node_outcomes.get(key)
    return key, str(label) if isinstance(label, str) and label.strip() else None


def _resolve_key(
    ivr_end_node_id: str | None,
    ivr_end_reason: str | None,
    dial_status: str | None,
    amd_status: str | None,
) -> tuple[str, str]:
    """Nodo y clave del desenlace, siguiendo el criterio de collect_send_masivos."""
    node = (ivr_end_node_id or "").strip()
    if node:
        reason = (ivr_end_reason or "").strip()
        return node, SYSTEM_REASON_TO_KEY.get(reason, reason or "abandono")

    # Sin `ivrEndNodeId`: Helena no registró dónde terminó. Se distinguen varios
    # escenarios, que para cobranza significan cosas muy distintas.

    # Descartada por la política de contacto: el número nunca se marcó. No es un
    # "no contestó" — la política existe por la Ley 2300, y un reporte que
    # mezcle ambos casos no permite demostrar que no se llamó fuera de horario.
    if dial_status == "OUT_OF_SCHEDULE":
        return CALL_LEVEL_NODE, "out_of_schedule"
    # Cancelada en la cola antes de marcarse (decisión del operador).
    if dial_status == "CANCELLED":
        return CALL_LEVEL_NODE, "cancelled"
    if dial_status != "ANSWER":
        return CALL_LEVEL_NODE, "no_answer"
    if amd_status != "HUMAN":
        # El AMD detectó máquina o buzón antes de entrar al IVR.
        return CALL_LEVEL_NODE, "voicemail"
    # Contestó una persona y entró al IVR, pero Helena no capturó el nodo: se
    # trata como abandono a nivel de llamada.
    return CALL_LEVEL_NODE, "abandono"
