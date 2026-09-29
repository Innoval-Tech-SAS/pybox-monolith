"""Helpers de redondeo, periodos de facturación y generación de referencias."""

from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal


def round_pesos(value: Decimal) -> int:
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def previous_period(now: datetime) -> tuple[int, int]:
    if now.month == 1:
        return now.year - 1, 12
    return now.year, now.month - 1


def period_bounds(period_year: int, period_month: int) -> tuple[datetime, datetime]:
    start = datetime(period_year, period_month, 1, tzinfo=timezone.utc)
    if period_month == 12:
        end = datetime(period_year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(period_year, period_month + 1, 1, tzinfo=timezone.utc)
    return start, end


def to_base36(value: int) -> str:
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    if value == 0:
        return "0"
    chars = []
    while value:
        value, rem = divmod(value, 36)
        chars.append(digits[rem])
    return "".join(reversed(chars)).upper()
