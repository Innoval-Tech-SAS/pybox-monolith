"""Base común de los providers de 360NRS (SMS/Email): request HTTP autenticado."""

import httpx

from core.config.logger import logger


class NRS360BaseProvider:
    """Request HTTP autenticado contra la API de 360NRS.

    Un `httpx.AsyncClient` por request abre/cierra conexión TLS cada vez; en
    un envío masivo (campañas) eso se vuelve el cuello de botella dominante.
    Las subclases (singletons vía `__new__`) crean un único `_http`
    reutilizado entre llamadas, y `_token` con la credencial ya resuelta —
    ver `NRS360EmailProvider`/`NRS360SmsProvider`.
    """

    _TIMEOUT_SECONDS = 10
    _http: httpx.AsyncClient
    _token: str

    async def _request(
        self,
        method: str,
        endpoint: str,
        token: str,
        json: dict | None = None,
        params: dict | None = None,
    ) -> httpx.Response:
        headers = {"Authorization": token}
        response = await self._http.request(
            method, f"{self.url}{endpoint}", json=json, params=params, headers=headers
        )
        response.raise_for_status()
        return response

    async def get_sending_events_report(
        self,
        sending_id: str,
        after_date: str | None = None,
        before_date: str | None = None,
    ) -> str:
        params: dict[str, str] = {}
        if after_date:
            params["afterDate"] = after_date
        if before_date:
            params["beforeDate"] = before_date
        try:
            response = await self._request(
                "GET",
                f"/sendings/{sending_id}/reports/events",
                self._token,
                params=params,
            )
            return response.text
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "[nrs360] events_report_http_error | sending_id=%s status=%s",
                sending_id,
                exc.response.status_code,
            )
            return ""

    @property
    def url(self) -> str:
        return "https://dashboard.360nrs.com/api/rest"
