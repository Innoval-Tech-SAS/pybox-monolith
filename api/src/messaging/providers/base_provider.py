import httpx


class NRS360BaseProvider:

    async def _request(
        self,
        method: str,
        url: str,
        token: str,
        json: dict | None = None,
        params: dict | None = None,
    ) -> httpx.Response:
        headers = {"Authorization": token}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.request(method, url, json=json, params=params, headers=headers)
        response.raise_for_status()
        return response
