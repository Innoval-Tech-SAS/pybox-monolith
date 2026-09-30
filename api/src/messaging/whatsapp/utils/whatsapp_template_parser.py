"""Extracción de las variables nombradas ({{variable}}) del cuerpo de una plantilla."""

import re
from typing import Any, NamedTuple

# Variables nombradas: {{nombre_variable}}, no posicionales. Coincide con el formato
# de creación forzado en whatsapp_client.create_template() (parameter_format=NAMED),
# igual convención de nombres que las columnas de deudores/creditos (snake_case).
_NAMED_PATTERN = re.compile(r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}")


class TemplateVariableSlot(NamedTuple):
    component: str
    name: str
    example: str


def extract_variable_slots(
    components: list[dict[str, Any]],
) -> list[TemplateVariableSlot]:
    """Extrae las variables nombradas ({{nombre}}) de los componentes BODY/HEADER que
    Meta devuelve para una plantilla aprobada, con su ejemplo si Meta lo trae en
    `example.body_text_named_params` / `example.header_text_named_params`.
    """
    slots: list[TemplateVariableSlot] = []
    for component in components:
        comp_type = str(component.get("type", "")).upper()
        if comp_type not in ("BODY", "HEADER"):
            continue
        text = component.get("text", "") or ""
        names = _ordered_unique(_NAMED_PATTERN.findall(text))
        if not names:
            continue

        examples = _extract_named_examples(component, comp_type)
        for name in names:
            slots.append(
                TemplateVariableSlot(
                    component=comp_type, name=name, example=examples.get(name, "")
                )
            )
    return slots


def _ordered_unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _extract_named_examples(
    component: dict[str, Any], comp_type: str
) -> dict[str, str]:
    example = component.get("example") or {}
    key = (
        "body_text_named_params" if comp_type == "BODY" else "header_text_named_params"
    )
    raw = example.get(key) or []
    return {
        item["param_name"]: str(item.get("example", ""))
        for item in raw
        if item.get("param_name")
    }
