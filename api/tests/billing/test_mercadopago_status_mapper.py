"""Unitario puro: mercadopago_order_status_to_attempt_status es una funcion sincrona
sobre un diccionario de modulo, sin dependencias externas. Tabla completa: cada status
de Order de MP debe mapear exactamente al PaymentAttemptStatus documentado, y
REFUNDED/CHARGED_BACK/desconocidos deben devolver None (se manejan aparte, no revierten
un pago ya confirmado)."""

import pytest

from billing.invoices.enums.invoice_enums import PaymentAttemptStatus
from billing.mercadopago.enums.mercadopago_enums import MercadoPagoOrderStatus
from billing.mercadopago.utils.mercadopago_status_mapper import (
    mercadopago_order_status_to_attempt_status,
)

_EXPECTED_MAPPING = {
    MercadoPagoOrderStatus.CREATED: PaymentAttemptStatus.ACTIVE,
    MercadoPagoOrderStatus.PROCESSING: PaymentAttemptStatus.PROCESSING,
    MercadoPagoOrderStatus.ACTION_REQUIRED: PaymentAttemptStatus.PROCESSING,
    MercadoPagoOrderStatus.PROCESSED: PaymentAttemptStatus.PAID,
    MercadoPagoOrderStatus.CANCELED: PaymentAttemptStatus.CANCELLED,
    MercadoPagoOrderStatus.EXPIRED: PaymentAttemptStatus.EXPIRED,
    MercadoPagoOrderStatus.FAILED: PaymentAttemptStatus.REJECTED,
}


class TestMercadopagoOrderStatusToAttemptStatusMappedStatuses:
    @pytest.mark.parametrize("order_status,expected", list(_EXPECTED_MAPPING.items()))
    def test_maps_to_expected_attempt_status(self, order_status, expected):
        assert (
            mercadopago_order_status_to_attempt_status(order_status.value) == expected
        )

    def test_all_mapped_statuses_are_covered_by_this_table(self):
        # Si se agrega un nuevo status al enum sin actualizar el mapper (o este test),
        # esto lo detecta en vez de dejar un status silenciosamente sin cubrir.
        unmapped_in_enum_but_not_terminal = (
            set(MercadoPagoOrderStatus)
            - set(_EXPECTED_MAPPING)
            - {
                MercadoPagoOrderStatus.REFUNDED,
                MercadoPagoOrderStatus.CHARGED_BACK,
            }
        )
        assert unmapped_in_enum_but_not_terminal == set()


class TestMercadopagoOrderStatusToAttemptStatusUnhandled:
    @pytest.mark.parametrize(
        "order_status",
        [MercadoPagoOrderStatus.REFUNDED, MercadoPagoOrderStatus.CHARGED_BACK],
    )
    def test_refund_and_chargeback_return_none(self, order_status):
        # La factura ya quedo PAID antes del reembolso/contracargo; eso se maneja como
        # un caso aparte (nota de credito / disputa), no como una transicion de intento.
        assert mercadopago_order_status_to_attempt_status(order_status.value) is None

    def test_unknown_string_returns_none_instead_of_raising(self):
        assert (
            mercadopago_order_status_to_attempt_status("algo-que-mp-nunca-documento")
            is None
        )

    def test_empty_string_returns_none(self):
        assert mercadopago_order_status_to_attempt_status("") is None
