"""Unitario puro (sin mocks, sin DB): current_period/last_n_months son funciones
sincronas sin dependencias externas, base de todos los agregados del dashboard de
facturacion -- un error de indice de mes/anio aqui rompe todos los reportes."""

from datetime import datetime, timezone

from billing.billing_dashboard.utils.billing_dashboard_utils import (
    current_period,
    last_n_months,
)


class TestCurrentPeriod:
    def test_returns_year_and_month_of_given_datetime(self):
        assert current_period(datetime(2026, 3, 15, tzinfo=timezone.utc)) == (2026, 3)

    def test_defaults_to_now_when_not_given(self):
        year, month = current_period()
        now = datetime.now(timezone.utc)
        assert (year, month) == (now.year, now.month)


class TestLastNMonths:
    def test_single_month_returns_just_current_period(self):
        assert last_n_months(1, datetime(2026, 8, 15, tzinfo=timezone.utc)) == [
            (2026, 8)
        ]

    def test_three_months_within_same_year(self):
        result = last_n_months(3, datetime(2026, 8, 15, tzinfo=timezone.utc))
        assert result == [(2026, 6), (2026, 7), (2026, 8)]

    def test_crosses_year_boundary(self):
        result = last_n_months(3, datetime(2026, 1, 15, tzinfo=timezone.utc))
        assert result == [(2025, 11), (2025, 12), (2026, 1)]

    def test_twelve_months_is_chronological_and_includes_current(self):
        result = last_n_months(12, datetime(2026, 8, 15, tzinfo=timezone.utc))
        assert len(result) == 12
        assert result[0] == (2025, 9)
        assert result[-1] == (2026, 8)
        # Estrictamente creciente en el tiempo, sin saltos ni repetidos.
        assert result == sorted(set(result))

    def test_december_reference_does_not_cross_into_next_year(self):
        result = last_n_months(2, datetime(2026, 12, 1, tzinfo=timezone.utc))
        assert result == [(2026, 11), (2026, 12)]
