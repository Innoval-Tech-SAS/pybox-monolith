import calendar
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def _assert_valid_timezone(tz_str: str) -> ZoneInfo:
    try:
        return ZoneInfo(tz_str)
    except (ZoneInfoNotFoundError, KeyError):
        raise ValueError(f"Timezone IANA inválido: {tz_str!r}")


def _parse_time_to_send(time_to_send: str) -> tuple[int, int, int]:
    parts = time_to_send.split(":")
    if len(parts) < 2:
        raise ValueError(f"time_to_send inválido: {time_to_send!r}. Formato: HH:MM o HH:MM:SS")
    h, m, s = int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0
    if not (0 <= h <= 23 and 0 <= m <= 59 and 0 <= s <= 59):
        raise ValueError(f"time_to_send fuera de rango: {time_to_send!r}")
    return h, m, s


def _to_utc(year: int, month: int, day: int, hour: int, minute: int, second: int, tz: ZoneInfo) -> datetime:
    local_dt = datetime(year, month, day, hour, minute, second, tzinfo=tz)
    return local_dt.astimezone(timezone.utc)


def _python_weekday_to_app(python_wd: int) -> int:
    # Python 0=Lun..6=Dom → App 0=Dom..6=Sáb (compatible pybox/JS)
    return (python_wd + 1) % 7


def _add_days(year: int, month: int, day: int, days: int) -> tuple[int, int, int]:
    d = datetime(year, month, day) + timedelta(days=days)
    return d.year, d.month, d.day


def _last_day_of_month(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def calculate_next_execution(
    periodicity: str,
    time_to_send: str,
    timezone_iana: str,
    days_of_week: list[int] | None = None,
    day_of_month: int | None = None,
    from_dt: datetime | None = None,
) -> datetime:
    p = periodicity.strip().lower()
    if p in ("once", "immediate"):
        raise ValueError(f"periodicity={periodicity!r} no admite recálculo de nextExecution")

    tz = _assert_valid_timezone(timezone_iana)
    h, m, s = _parse_time_to_send(time_to_send)

    now_utc = (from_dt or datetime.now(timezone.utc)).replace(tzinfo=timezone.utc)
    now_local = now_utc.astimezone(tz)
    y, mo, d = now_local.year, now_local.month, now_local.day
    from_ms = now_utc.timestamp()

    if p == "daily":
        candidate = _to_utc(y, mo, d, h, m, s, tz)
        if candidate.timestamp() > from_ms:
            return candidate
        ny, nmo, nd = _add_days(y, mo, d, 1)
        return _to_utc(ny, nmo, nd, h, m, s, tz)

    if p == "weekly":
        target_days = sorted(set(max(0, min(6, dw)) for dw in (days_of_week or [])))
        for i in range(14):
            cy, cmo, cd = _add_days(y, mo, d, i)
            app_wd = _python_weekday_to_app(datetime(cy, cmo, cd).weekday())
            if target_days and app_wd not in target_days:
                continue
            candidate = _to_utc(cy, cmo, cd, h, m, s, tz)
            if candidate.timestamp() > from_ms:
                return candidate
        # Fallback: mismo día la próxima semana
        fy, fmo, fd = _add_days(y, mo, d, 7)
        return _to_utc(fy, fmo, fd, h, m, s, tz)

    if p == "monthly":
        target_day = day_of_month or d
        this_month_day = min(target_day, _last_day_of_month(y, mo))
        candidate = _to_utc(y, mo, this_month_day, h, m, s, tz)
        if candidate.timestamp() > from_ms:
            return candidate
        next_mo = mo + 1
        next_yr = y
        if next_mo > 12:
            next_mo = 1
            next_yr += 1
        next_day = min(target_day, _last_day_of_month(next_yr, next_mo))
        return _to_utc(next_yr, next_mo, next_day, h, m, s, tz)

    raise ValueError(f"periodicity={periodicity!r} no soportada")
