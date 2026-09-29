"""Resolución de fechas relativas (@now, semana/mes actual) para filtros dinámicos."""

import re
from datetime import date, datetime, timedelta, timezone
from typing import Any

_OFFSET_RE = re.compile(r"^@now([+-]\d+)d$")


def _week_bounds(today: date) -> tuple[date, date]:
    start = today - timedelta(days=today.weekday())
    return start, start + timedelta(days=6)


def _month_bounds(today: date) -> tuple[date, date]:
    start = today.replace(day=1)
    next_month = (
        start.replace(year=start.year + 1, month=1)
        if start.month == 12
        else start.replace(month=start.month + 1)
    )
    return start, next_month - timedelta(days=1)


def resolve_relative_token(token: str) -> datetime | date:
    now = datetime.now(timezone.utc)
    today = now.date()
    if token == "@now":
        return now
    if token == "@today":
        return today
    if token == "@week_start":
        return _week_bounds(today)[0]
    if token == "@week_end":
        return _week_bounds(today)[1]
    if token == "@month_start":
        return _month_bounds(today)[0]
    if token == "@month_end":
        return _month_bounds(today)[1]
    match = _OFFSET_RE.match(token)
    if match:
        return now + timedelta(days=int(match.group(1)))
    raise ValueError(f"Token de fecha relativa desconocido: '{token}'.")


def resolve_filter_value(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("@"):
        return resolve_relative_token(value)
    if isinstance(value, list):
        return [resolve_filter_value(v) for v in value]
    return value
