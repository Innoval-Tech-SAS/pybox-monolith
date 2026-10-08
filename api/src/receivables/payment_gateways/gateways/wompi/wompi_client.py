"""Cliente HTTP crudo a la API de Wompi (sin conocer organizaciones ni cuotas)."""

from typing import Any

from core.payment_gateways.gateway_http_client import GatewayHttpClient

_SANDBOX_BASE = "https://sandbox.wompi.co/v1"
_PRODUCTION_BASE = "https://production.wompi.co/v1"


class WompiClient(GatewayHttpClient):
    """Cliente HTTP crudo a la API de Wompi. No sabe nada de organizaciones ni de
    cuotas — cada metodo recibe explicitamente la llave y el ambiente a usar, porque
    cada organizacion tiene las suyas (a diferencia de Mercado Pago/Bold en billing, no
    hay una sola cuenta por pais: es una por organizacion, ver
    `OrganizationGatewayCredentialService`)."""

    _LOG_TAG = "wompi"

    @staticmethod
    def _base_url(environment: str) -> str:
        return _PRODUCTION_BASE if environment == "production" else _SANDBOX_BASE

    async def get_merchant_info(
        self, public_key: str, environment: str
    ) -> dict[str, Any]:
        """GET /merchants/info (llave publica en header) — trae los tokens de
        aceptacion vigentes (skill `wompi-gateway`, Paso 3). El endpoint viejo
        (`GET /merchants/:public_key`, llave en la URL) se deprecara el 31/oct/2026;
        este ya implementa el nuevo desde el dia uno."""
        response = await self._http.get(
            f"{self._base_url(environment)}/merchants/info",
            headers={"x-merchant-public-key": public_key},
        )
        self._log_error(response, "get_merchant_info")
        response.raise_for_status()
        return response.json()

    async def create_transaction(
        self, private_key: str, environment: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        response = await self._http.post(
            f"{self._base_url(environment)}/transactions",
            json=payload,
            headers={"Authorization": f"Bearer {private_key}"},
        )
        self._log_error(response, "create_transaction")
        response.raise_for_status()
        return response.json()

    async def get_transaction(
        self, private_key: str, environment: str, transaction_id: str
    ) -> dict[str, Any]:
        response = await self._http.get(
            f"{self._base_url(environment)}/transactions/{transaction_id}",
            headers={"Authorization": f"Bearer {private_key}"},
        )
        self._log_error(response, f"get_transaction transaction_id={transaction_id}")
        response.raise_for_status()
        return response.json()

    async def tokenize_card(
        self, public_key: str, environment: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """POST /tokens/cards con llave PUBLICA — la tarjeta pasa por este backend
        directamente (API directa, no widget), lo que exige cumplimiento PCI SAQ A-EP
        (skill `wompi-gateway`, Paso 5). Usar solo si hay una razon fuerte para no usar
        el widget en modo tokenize (PCI SAQ A, mas simple)."""
        response = await self._http.post(
            f"{self._base_url(environment)}/tokens/cards",
            json=payload,
            headers={"Authorization": f"Bearer {public_key}"},
        )
        self._log_error(response, "tokenize_card")
        response.raise_for_status()
        return response.json()

    async def tokenize_nequi(
        self, public_key: str, environment: str, phone_number: str
    ) -> dict[str, Any]:
        response = await self._http.post(
            f"{self._base_url(environment)}/tokens/nequi",
            json={"phone_number": phone_number},
            headers={"Authorization": f"Bearer {public_key}"},
        )
        self._log_error(response, "tokenize_nequi")
        response.raise_for_status()
        return response.json()

    async def create_payment_source(
        self, private_key: str, environment: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """POST /payment_sources con llave PRIVADA desde el backend (skill
        `wompi-gateway`, Paso 5.2) — nunca desde el frontend."""
        response = await self._http.post(
            f"{self._base_url(environment)}/payment_sources",
            json=payload,
            headers={"Authorization": f"Bearer {private_key}"},
        )
        self._log_error(response, "create_payment_source")
        response.raise_for_status()
        return response.json()

    async def list_pse_financial_institutions(
        self, private_key: str, environment: str
    ) -> dict[str, Any]:
        response = await self._http.get(
            f"{self._base_url(environment)}/pse/financial_institutions",
            headers={"Authorization": f"Bearer {private_key}"},
        )
        self._log_error(response, "list_pse_financial_institutions")
        response.raise_for_status()
        return response.json()
