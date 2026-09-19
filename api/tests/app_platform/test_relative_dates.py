"""Unit tests puros para la resolución de fechas relativas (`@today`, `@month_start`,
`@now+30d`, etc.) usadas como valores de filtro en segmentos/reportes."""

from datetime import date, datetime, timedelta, timezone

import pytest

from app_platform.schema_manager.utils.relative_dates import (
    _month_bounds,
    _week_bounds,
    resolve_filter_value,
    resolve_relative_token,
)


class TestResolveRelativeToken:
    def test_now_returns_datetime_utc(self):
        result = resolve_relative_token("@now")
        assert isinstance(result, datetime)
        assert result.tzinfo is not None

    def test_today_returns_date(self):
        result = resolve_relative_token("@today")
        assert result == datetime.now(timezone.utc).date()

    def test_week_start_is_monday(self):
        result = resolve_relative_token("@week_start")
        assert result.weekday() == 0

    def test_week_end_is_sunday(self):
        result = resolve_relative_token("@week_end")
        assert result.weekday() == 6

    def test_week_start_and_end_are_six_days_apart(self):
        start = resolve_relative_token("@week_start")
        end = resolve_relative_token("@week_end")
        assert (end - start).days == 6

    def test_month_start_is_first_day(self):
        result = resolve_relative_token("@month_start")
        assert result.day == 1

    def test_month_end_is_last_day_of_month(self):
        start = resolve_relative_token("@month_start")
        end = resolve_relative_token("@month_end")
        # El día siguiente al fin de mes debe caer en el mes siguiente.
        assert (end + timedelta(days=1)).day == 1

    def test_offset_positive_days(self):
        now = datetime.now(timezone.utc)
        result = resolve_relative_token("@now+30d")
        assert (result - now).days == 30

    def test_offset_negative_days(self):
        result = resolve_relative_token("@now-15d")
        now = datetime.now(timezone.utc)
        assert (now - result).days == 15

    def test_unknown_token_raises(self):
        with pytest.raises(ValueError, match="Token de fecha relativa desconocido"):
            resolve_relative_token("@bogus_token")

    def test_malformed_offset_raises(self):
        with pytest.raises(ValueError):
            resolve_relative_token("@now+d")


class TestResolveFilterValue:
    def test_plain_string_passes_through(self):
        assert resolve_filter_value("CO") == "CO"

    def test_number_passes_through(self):
        assert resolve_filter_value(42) == 42

    def test_relative_token_resolved(self):
        result = resolve_filter_value("@today")
        assert result == datetime.now(timezone.utc).date()

    def test_list_of_relative_tokens_resolved_for_between(self):
        result = resolve_filter_value(["@now-1d", "@now+1d"])
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(v, datetime) for v in result)

    def test_mixed_list_only_resolves_at_signs(self):
        result = resolve_filter_value(["CO", "@today"])
        assert result[0] == "CO"
        assert result[1] == datetime.now(timezone.utc).date()


class TestMonthBoundsYearRollover:
    def test_december_rolls_into_next_year(self):
        start, end = _month_bounds(date(2024, 12, 15))
        assert start == date(2024, 12, 1)
        assert end == date(2024, 12, 31)

    def test_non_december_month_end(self):
        start, end = _month_bounds(date(2024, 2, 10))
        # 2024 es bisiesto: febrero tiene 29 días.
        assert start == date(2024, 2, 1)
        assert end == date(2024, 2, 29)

    def test_non_leap_february(self):
        _, end = _month_bounds(date(2023, 2, 10))
        assert end == date(2023, 2, 28)


class TestWeekBoundsTimezoneEdge:
    def test_week_bounds_of_a_known_sunday(self):
        # 2024-01-07 es domingo -> la semana debe empezar el 2024-01-01 (lunes).
        start, end = _week_bounds(date(2024, 1, 7))
        assert start == date(2024, 1, 1)
        assert end == date(2024, 1, 7)

    def test_week_bounds_of_a_known_monday(self):
        start, end = _week_bounds(date(2024, 1, 1))
        assert start == date(2024, 1, 1)
        assert end == date(2024, 1, 7)
