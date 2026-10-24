"""Cliente HTTP crudo a la API de pagos en línea de Bold."""

from typing import Any

from core.payment_gateways.gateway_http_client import GatewayHttpClient

_BASE_URL = "https://api.online.payments.bold.co"


def _auth_header(identity_key: str) -> dict[str, str]:
    """Bold autentica con el header `Authorization`, cuyo VALOR es el string
    `"x-api-key <identity_key>"` -- no un header literal `x-api-key` (confirmado
    contra developers.bold.co/pagos-en-linea/api-de-pagos-en-linea/integracion)."""
    return {"Authorization": f"x-api-key {identity_key}"}


class BoldClient(GatewayHttpClient):
    """Cliente HTTP crudo a la API de pagos en línea de Bold
    (developers.bold.co/pagos-en-linea/api-de-pagos-en-linea). Una sola base URL para
    sandbox y producción -- el ambiente lo determina la llave de identidad usada
    (sandbox vs. producción), no el host. No sabe nada de organizaciones ni de cuotas,
    igual que `WompiClient` -- cada método recibe explícitamente la llave a usar."""

    _LOG_TAG = "bold"

    async def create_payment_intent(
        self, identity_key: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        response = await self._http.post(
            f"{_BASE_URL}/v1/payment-intent",
            json=payload,
            headers=_auth_header(identity_key),
        )
        self._log_error(response, "create_payment_intent")
        response.raise_for_status()
        return response.json()

    async def create_payment(
        self, identity_key: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        response = await self._http.post(
            f"{_BASE_URL}/v1/payment",
            json=payload,
            headers=_auth_header(identity_key),
        )
        self._log_error(response, "create_payment")
        response.raise_for_status()
        return response.json()

    async def get_payment_status(
        self, identity_key: str, reference_id: str
    ) -> dict[str, Any]:
        response = await self._http.get(
            f"{_BASE_URL}/v1/payment/{reference_id}",
            headers=_auth_header(identity_key),
        )
        self._log_error(response, f"get_payment_status reference_id={reference_id}")
        response.raise_for_status()
        return response.json()

    async def list_pse_banks(self, identity_key: str) -> dict[str, Any]:
        response = await self._http.get(
            f"{_BASE_URL}/v1/payment/pse/banks",
            headers=_auth_header(identity_key),
        )
        self._log_error(response, "list_pse_banks")
        response.raise_for_status()
        return response.json()
