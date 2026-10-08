"""Unit test puro para `last_n_months`: la ventana de meses del gráfico de envíos
mensuales del dashboard. El caso interesante es el rollover de año (enero hacia
atrás debe caer en diciembre del año anterior)."""

from datetime import datetime, timezone

from app_platform.dashboard.utils.dashboard_utils import last_n_months


class TestLastNMonths:
    def test_includes_current_month_as_last_element(self):
        now = datetime(2024, 6, 15, tzinfo=timezone.utc)
        months = last_n_months(3, now)
        assert months[-1] == (2024, 6)

    def test_chronological_order(self):
        now = datetime(2024, 6, 15, tzinfo=timezone.utc)
        months = last_n_months(3, now)
        assert months == [(2024, 4), (2024, 5), (2024, 6)]

    def test_year_rollover_going_backwards(self):
        now = datetime(2024, 2, 10, tzinfo=timezone.utc)
        months = last_n_months(3, now)
        assert months == [(2023, 12), (2024, 1), (2024, 2)]

    def test_full_twelve_month_window_from_january(self):
        now = datetime(2024, 1, 1, tzinfo=timezone.utc)
        months = last_n_months(12, now)
        assert months[0] == (2023, 2)
        assert months[-1] == (2024, 1)
        assert len(months) == 12

    def test_defaults_to_now_when_reference_omitted(self):
        months = last_n_months(1)
        current = datetime.now(timezone.utc)
        assert months == [(current.year, current.month)]
