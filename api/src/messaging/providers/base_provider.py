import httpx


class NRS360BaseProvider:


    async def _request(
        self,
        method: str,
        endpoint: str,
        token: str,
        json: dict | None = None,
        params: dict | None = None,
    ) -> httpx.Response:
        headers = {"Authorization": token}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.request(
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
        response = await self._request(
            "GET", f"/sendings/{sending_id}/reports/events", self._token, params=params
        )
        return response.text


    @property
    def url(self) -> str:
        return "https://dashboard.360nrs.com/api/rest"