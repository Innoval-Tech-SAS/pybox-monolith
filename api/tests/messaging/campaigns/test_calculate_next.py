"""Tests puros de `calculate_next.py`: cálculo de la próxima ejecución de una
campaña recurrente. El riesgo real está en los bordes -- hora ya pasada hoy vs.
mañana, fin de mes con day_of_month=31 en meses cortos, y la conversión de
zona horaria local -> UTC (un candidato calculado en hora local puede caer del
otro lado de la medianoche en UTC).
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from messaging.campaigns.utils.calculate_next import calculate_next_execution, project_occurrences


class TestCalculateNextExecutionDaily:
    def test_time_still_ahead_today_returns_today(self):
        # 10:00 UTC en Bogota (UTC-5) = 05:00 local -- 08:00 local todavia no paso.
        from_dt = datetime(2026, 8, 19, 10, 0, tzinfo=timezone.utc)
        result = calculate_next_execution(
            periodicity="diario", time_to_send="08:00", timezone_iana="America/Bogota", from_dt=from_dt
        )
        assert result.astimezone(ZoneInfo("America/Bogota")).date() == from_dt.astimezone(ZoneInfo("America/Bogota")).date()
        assert result > from_dt

    def test_time_already_passed_today_rolls_to_tomorrow(self):
        # 20:00 UTC en Bogota = 15:00 local -- 08:00 local ya paso hoy.
        from_dt = datetime(2026, 8, 19, 20, 0, tzinfo=timezone.utc)
        result = calculate_next_execution(
            periodicity="diario", time_to_send="08:00", timezone_iana="America/Bogota", from_dt=from_dt
        )
        local_today = from_dt.astimezone(ZoneInfo("America/Bogota")).date()
        local_result = result.astimezone(ZoneInfo("America/Bogota")).date()
        assert (local_result - local_today).days == 1
        assert result.astimezone(ZoneInfo("America/Bogota")).hour == 8

    def test_timezone_conversion_crosses_utc_day_boundary(self):
        # 23:30 local en Bogota (UTC-5) el 19 -> 04:30 UTC del 20: la fecha UTC no
        # coincide con la fecha local, prueba real de que la conversion es correcta.
        from_dt = datetime(2026, 8, 19, 10, 0, tzinfo=timezone.utc)  # 05:00 local
        result = calculate_next_execution(
            periodicity="diario", time_to_send="23:30", timezone_iana="America/Bogota", from_dt=from_dt
        )
        assert result.tzinfo == timezone.utc
        assert result.astimezone(ZoneInfo("America/Bogota")).day == 19
        assert result.day == 20  # ya cruzo a UTC del dia siguiente
        assert result.hour == 4
        assert result.minute == 30


class TestCalculateNextExecutionWeekly:
    def test_next_matching_weekday_within_two_weeks(self):
        # 19 ago 2026 es miercoles (app_wd=3). Pide viernes (app_wd=5).
        from_dt = datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)
        result = calculate_next_execution(
            periodicity="semanal", time_to_send="09:00", timezone_iana="UTC",
            days_of_week=[5], from_dt=from_dt,
        )
        assert result.weekday() == 4  # python: 4=viernes
        assert result > from_dt

    def test_no_days_of_week_means_unconstrained_returns_next_time_slot(self):
        # Sin days_of_week no hay restriccion de dia: se comporta como daily,
        # devolviendo la proxima vez que ocurra time_to_send (09:00 ya paso hoy
        # a las 12:00 -- rueda a manana).
        from_dt = datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)
        result = calculate_next_execution(
            periodicity="semanal", time_to_send="09:00", timezone_iana="UTC",
            days_of_week=None, from_dt=from_dt,
        )
        assert (result.date() - from_dt.date()).days == 1
        assert result.hour == 9

    def test_out_of_range_weekday_values_are_clamped(self):
        # days_of_week con valores invalidos (-1, 99) no debe reventar: se clampean a 0/6.
        from_dt = datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)
        result = calculate_next_execution(
            periodicity="semanal", time_to_send="09:00", timezone_iana="UTC",
            days_of_week=[-1, 99], from_dt=from_dt,
        )
        assert result is not None


class TestCalculateNextExecutionMonthly:
    def test_day_still_ahead_this_month(self):
        from_dt = datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc)
        result = calculate_next_execution(
            periodicity="mensual", time_to_send="09:00", timezone_iana="UTC",
            day_of_month=20, from_dt=from_dt,
        )
        assert result.month == 8
        assert result.day == 20

    def test_day_already_passed_rolls_to_next_month(self):
        from_dt = datetime(2026, 8, 25, 12, 0, tzinfo=timezone.utc)
        result = calculate_next_execution(
            periodicity="mensual", time_to_send="09:00", timezone_iana="UTC",
            day_of_month=20, from_dt=from_dt,
        )
        assert result.month == 9
        assert result.day == 20

    def test_day_31_clamps_to_last_day_of_short_month(self):
        # Febrero 2027 (no bisiesto) solo tiene 28 dias -- day_of_month=31 debe
        # clampear a 28, no reventar ni desbordar a marzo.
        from_dt = datetime(2027, 1, 30, 12, 0, tzinfo=timezone.utc)
        result = calculate_next_execution(
            periodicity="mensual", time_to_send="09:00", timezone_iana="UTC",
            day_of_month=31, from_dt=from_dt,
        )
        assert result.month == 1
        assert result.day == 31

        # Pasado ya el 30 de enero, la siguiente cae en febrero clampeada a 28.
        from_dt2 = datetime(2027, 2, 1, 12, 0, tzinfo=timezone.utc)
        result2 = calculate_next_execution(
            periodicity="mensual", time_to_send="09:00", timezone_iana="UTC",
            day_of_month=31, from_dt=from_dt2,
        )
        assert result2.month == 2
        assert result2.day == 28

    def test_no_day_of_month_defaults_to_current_day(self):
        from_dt = datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc)
        result = calculate_next_execution(
            periodicity="mensual", time_to_send="09:00", timezone_iana="UTC",
            day_of_month=None, from_dt=from_dt,
        )
        assert result.day == 5


class TestCalculateNextExecutionValidation:
    @pytest.mark.parametrize("periodicity", ["una_vez", "inmediato", "UNA_VEZ", "Inmediato"])
    def test_once_and_immediate_are_rejected(self, periodicity):
        with pytest.raises(ValueError):
            calculate_next_execution(periodicity=periodicity, time_to_send="09:00", timezone_iana="UTC")

    def test_unsupported_periodicity_raises(self):
        with pytest.raises(ValueError):
            calculate_next_execution(periodicity="yearly", time_to_send="09:00", timezone_iana="UTC")

    def test_invalid_timezone_raises(self):
        with pytest.raises(ValueError, match="Timezone IANA inválido"):
            calculate_next_execution(periodicity="diario", time_to_send="09:00", timezone_iana="Not/AZone")

    def test_invalid_time_to_send_format_raises(self):
        with pytest.raises(ValueError, match="time_to_send inválido"):
            calculate_next_execution(periodicity="diario", time_to_send="0900", timezone_iana="UTC")

    def test_time_to_send_out_of_range_raises(self):
        with pytest.raises(ValueError, match="fuera de rango"):
            calculate_next_execution(periodicity="diario", time_to_send="25:00", timezone_iana="UTC")

    def test_time_to_send_with_seconds_is_parsed(self):
        from_dt = datetime(2026, 8, 19, 0, 0, tzinfo=timezone.utc)
        result = calculate_next_execution(
            periodicity="diario", time_to_send="08:30:15", timezone_iana="UTC", from_dt=from_dt
        )
        assert result.hour == 8
        assert result.minute == 30
        assert result.second == 15


class TestProjectOccurrences:
    def test_daily_projects_one_per_day_within_range(self):
        start = datetime(2026, 8, 19, 0, 0, tzinfo=timezone.utc)
        end = datetime(2026, 8, 22, 0, 0, tzinfo=timezone.utc)
        occurrences = project_occurrences(
            periodicity="diario", time_to_send="09:00", timezone_iana="UTC",
            range_start=start, range_end=end,
        )
        assert len(occurrences) == 3  # 19, 20, 21 a las 09:00 (22 a las 09:00 excede el rango)
        assert all(o.hour == 9 for o in occurrences)
        # ordenadas y estrictamente crecientes
        assert occurrences == sorted(occurrences)

    def test_empty_range_returns_no_occurrences(self):
        start = datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)
        end = datetime(2026, 8, 19, 13, 0, tzinfo=timezone.utc)
        occurrences = project_occurrences(
            periodicity="diario", time_to_send="09:00", timezone_iana="UTC",
            range_start=start, range_end=end,
        )
        assert occurrences == []

    def test_max_occurrences_caps_the_result(self):
        start = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2030, 1, 1, 0, 0, tzinfo=timezone.utc)
        occurrences = project_occurrences(
            periodicity="diario", time_to_send="09:00", timezone_iana="UTC",
            range_start=start, range_end=end, max_occurrences=5,
        )
        assert len(occurrences) == 5

    def test_once_periodicity_is_rejected(self):
        start = datetime(2026, 8, 19, tzinfo=timezone.utc)
        end = datetime(2026, 8, 20, tzinfo=timezone.utc)
        with pytest.raises(ValueError):
            project_occurrences(
                periodicity="once", time_to_send="09:00", timezone_iana="UTC",
                range_start=start, range_end=end,
            )
