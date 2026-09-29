from datetime import datetime, timezone


def current_period(now: datetime | None = None) -> tuple[int, int]:
    reference = now or datetime.now(timezone.utc)
    return reference.year, reference.month


def last_n_months(n: int, now: datetime | None = None) -> list[tuple[int, int]]:
    """Lista de (anio, mes) de los ultimos n meses, en orden cronologico,
    incluyendo el mes actual.
    """
    reference = now or datetime.now(timezone.utc)
    year, month = reference.year, reference.month
    months: list[tuple[int, int]] = []
    for _ in range(n):
        months.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return list(reversed(months))
