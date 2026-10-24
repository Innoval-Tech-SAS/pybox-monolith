"""Cliente HTTP crudo a la API de PayU Latam (Payments API y Reports API)."""

from typing import Any

from core.payment_gateways.gateway_http_client import GatewayHttpClient

_PAYMENTS_URL = {
    "production": "https://api.payulatam.com/payments-api/4.0/service.cgi",
    "sandbox": "https://sandbox.api.payulatam.com/payments-api/4.0/service.cgi",
}
_REPORTS_URL = {
    "production": "https://api.payulatam.com/reports-api/4.0/service.cgi",
    "sandbox": "https://sandbox.api.payulatam.com/reports-api/4.0/service.cgi",
}


class PayUClient(GatewayHttpClient):
    """Cliente HTTP crudo a PayU Latam (developers.payulatam.com) -- a diferencia de
    Bold/Wompi, el ambiente (sandbox/producción) SÍ determina el host (no solo la
    llave), por eso cada método recibe `environment` explícitamente. No sabe nada de
    organizaciones ni de cuotas, igual que `BoldClient`/`WompiClient`."""

    _LOG_TAG = "payu"

    async def submit_transaction(
        self, environment: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        response = await self._http.post(_PAYMENTS_URL[environment], json=payload)
        self._log_error(response, "submit_transaction")
        response.raise_for_status()
        return response.json()

    async def get_banks_list(
        self, environment: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        response = await self._http.post(_PAYMENTS_URL[environment], json=payload)
        self._log_error(response, "get_banks_list")
        response.raise_for_status()
        return response.json()

    async def order_detail_by_reference_code(
        self, environment: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        response = await self._http.post(_REPORTS_URL[environment], json=payload)
        self._log_error(response, "order_detail_by_reference_code")
        response.raise_for_status()
        return response.json()
