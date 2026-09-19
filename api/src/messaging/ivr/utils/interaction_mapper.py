"""Traducción del payload de Helena al modelo de Pybox.

Dos problemas concretos que resuelve este módulo:

1. **Fechas sin zona.** Helena serializa las fechas de `interaction` como
   `"YYYY-MM-DD HH:mm:ss"` en hora *local de su servidor*
   (`webhooks.service.ts:formatLocalDate`), no en ISO-8601 con offset. Las
   columnas del template son `DateTime(timezone=True)`, así que hay que
   asumir una zona: `HELENA_TIMEZONE` (default `America/Bogota`, la misma con
   la que corre el contenedor de la API). `meta.occurredAt` sí es ISO y se
   prefiere cuando está disponible.

2. **Estado visual.** Helena no reporta un "estado" de la llamada, sino campos
   sueltos (`amdStatus`, `dialStatus`, `transferred`, …). El estado se deriva,
   siguiendo el mismo criterio que `iris`
   (`call-monitor-projection.service.ts:deriveStatus`).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from core.config.logger import logger
from core.tools.config_tools import get_or_default
from messaging.ivr.constants.helena_defaults import DEFAULT_TIMEZONE
from messaging.ivr.enums.ivr_enums import IvrCallStatus

_HELENA_DATE_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M")

#: `dialStatus` con los que Helena marca una llamada que nunca llegó a marcarse:
#: cancelación manual de la cola y descarte por política de contacto
#: (`interactions.repository.ts:bulkCancel` / `bulkMarkOutOfSchedule`). Ninguno
#: trae `endedAt`, así que sin esto la llamada quedaría "sonando" para siempre.
_CANCELLED_DIAL_STATUSES = frozenset({"CANCELLED", "OUT_OF_SCHEDULE"})

#: Asterisk reporta `NOANSWER` (sin guion bajo), pero el cierre por timeout de
#: Helena escribe `NO_ANSWER` (`interactions.service.ts:markAsStaleTimedOut`).
#: Se aceptan ambos o esas llamadas se contarían como fallidas.
_NO_ANSWER_DIAL_STATUSES = frozenset({"NOANSWER", "NO_ANSWER"})


def _helena_tz() -> ZoneInfo:
    name = get_or_default("HELENA_TIMEZONE", DEFAULT_TIMEZONE)
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        logger.warning("[ivr] HELENA_TIMEZONE inválida=%s, se usa %s", name, DEFAULT_TIMEZONE)
        return ZoneInfo(DEFAULT_TIMEZONE)


def parse_helena_datetime(value: Any) -> datetime | None:
    """Convierte una fecha de Helena a `datetime` con zona.

    Acepta tanto el formato local `"YYYY-MM-DD HH:mm:ss"` como ISO-8601 (que es
    lo que trae `meta.occurredAt`). Devuelve `None` ante cualquier valor que no
    se pueda interpretar: una fecha ilegible no debe tumbar la ingesta.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=_helena_tz())

    text = str(value).strip()
    if not text:
        return None

    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=_helena_tz())
    except ValueError:
        pass

    for fmt in _HELENA_DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=_helena_tz())
        except ValueError:
            continue

    logger.warning("[ivr] fecha de Helena no interpretable=%r", text)
    return None


def as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def as_str(value: Any, max_length: int | None = None) -> str | None:
    """Normaliza a texto no vacío, recortado al ancho de la columna."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text[:max_length] if max_length else text


def derive_status(
    *,
    ended_at: datetime | None,
    dial_status: str | None,
    transferred: bool,
    transfer_dial_status: str | None,
    transfer_started_at: datetime | None,
    amd_status: str | None,
    has_ivr_activity: bool,
    cancelled: bool = False,
) -> IvrCallStatus:
    """Estado visual de la llamada a partir de los campos acumulados.

    El orden importa: primero lo terminal, después lo más específico del
    recorrido (transferencia > IVR > AMD), y `RINGING` como caso base.
    """
    # El `dialStatus` se comprueba además del flag porque los eventos pueden
    # llegar desordenados: una vez Helena marcó la llamada como cancelada o
    # fuera de horario, ningún evento posterior debe devolverla a "en curso".
    if cancelled or dial_status in _CANCELLED_DIAL_STATUSES:
        return IvrCallStatus.CANCELLED

    if ended_at is not None:
        if dial_status in _NO_ANSWER_DIAL_STATUSES:
            return IvrCallStatus.NO_ANSWER
        if transferred or transfer_dial_status == "ANSWER":
            return IvrCallStatus.COMPLETED
        if dial_status == "ANSWER":
            return IvrCallStatus.COMPLETED
        return IvrCallStatus.FAILED

    if transfer_started_at is not None:
        return IvrCallStatus.TRANSFERRING
    if has_ivr_activity:
        return IvrCallStatus.IN_IVR
    if amd_status == "HUMAN":
        return IvrCallStatus.HUMAN_DETECTED
    if amd_status in ("MACHINE", "NOTSURE"):
        return IvrCallStatus.MACHINE_DETECTED

    return IvrCallStatus.RINGING


def append_unique(existing: list | None, entry: dict[str, Any] | None) -> list:
    """Añade una entrada a un array acumulado evitando duplicados exactos.

    Los webhooks se despachan con `Promise.allSettled` y pueden repetirse; sin
    esta deduplicación un reintento de red duplicaría un dígito DTMF.
    """
    items = list(existing or [])
    if entry is None:
        return items
    if entry in items:
        return items
    items.append(entry)
    return items
