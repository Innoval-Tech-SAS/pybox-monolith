"""Cliente HTTP crudo a la API REST (ApiFy) de ePayco."""

from typing import Any

from core.payment_gateways.gateway_http_client import GatewayHttpClient

_BASE_URL = "https://apify.epayco.co"


class EpaycoClient(GatewayHttpClient):
    """Cliente HTTP crudo a la ApiFy de ePayco (api.epayco.co, colección oficial de
    Postman) -- una sola base URL para sandbox y producción, el ambiente lo determina
    el campo `testMode` de cada payload, no el host ni la llave (a diferencia de
    PayU). Toda llamada salvo `login` exige el JWT que éste devuelve, como
    `Authorization: Bearer <token>` -- no hay equivalente a la `identity_key`/
    `private_key` de Bold/Wompi que viaje directo en un header propio."""

    _LOG_TAG = "epayco"

    async def login(self, public_key: str, private_key: str) -> dict[str, Any]:
        response = await self._http.post(
            f"{_BASE_URL}/login", auth=(public_key, private_key)
        )
        self._log_error(response, "login")
        response.raise_for_status()
        return response.json()

    async def create_pse_transaction(
        self, token: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        response = await self._http.post(
            f"{_BASE_URL}/payment/process/pse",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        self._log_error(response, "create_pse_transaction")
        response.raise_for_status()
        return response.json()

    async def get_pse_banks(self, token: str) -> dict[str, Any]:
        response = await self._http.get(
            f"{_BASE_URL}/payment/pse/banks",
            headers={"Authorization": f"Bearer {token}"},
        )
        self._log_error(response, "get_pse_banks")
        response.raise_for_status()
        return response.json()

    async def create_daviplata_transaction(
        self, token: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        response = await self._http.post(
            f"{_BASE_URL}/payment/process/daviplata",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        self._log_error(response, "create_daviplata_transaction")
        response.raise_for_status()
        return response.json()

    async def confirm_daviplata_transaction(
        self, token: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        response = await self._http.post(
            f"{_BASE_URL}/payment/confirm/daviplata",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        self._log_error(response, "confirm_daviplata_transaction")
        response.raise_for_status()
        return response.json()

    async def get_transaction_detail(
        self, token: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """`GET /transaction/detail` lleva un body JSON con el filtro -- inusual para
        un GET, pero es lo que exige la API (confirmado en la colección oficial de
        Postman), por eso se usa `request()` en vez de `get()`."""
        response = await self._http.request(
            "GET",
            f"{_BASE_URL}/transaction/detail",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        self._log_error(response, "get_transaction_detail")
        response.raise_for_status()
        return response.json()
