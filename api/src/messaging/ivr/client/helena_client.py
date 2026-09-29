from __future__ import annotations

from typing import Any, Literal

import httpx

from messaging.ivr.config.helena_config import HelenaConfig


class HelenaClient:
    """Cliente HTTP asíncrono para la API externa de Helena (llamadas IVR).

    Portado del cliente síncrono de `collect_send_masivos` al stack async del
    template (httpx). La autorización usa `Authorization: Bearer <api_key>`,
    con la key tomada de la variable de entorno `HELENA_API_TOKEN`.
    """

    def __init__(self, cfg: HelenaConfig) -> None:
        self._cfg = cfg
        self._base_url = cfg.base_url.rstrip("/")

    # ── Llamadas ──────────────────────────────────────────────────────────────

    async def send_bulk_json(
        self,
        payload: dict[str, Any],
        scheduled_date: str = "",
        scheduled_time: str = "",
    ) -> dict[str, Any]:
        """Envía llamadas masivas a Helena en formato bulk JSON (`POST /calls/bulk`).

        `scheduled_date` / `scheduled_time` se dejan vacíos cuando el template ya
        disparó la campaña a su hora (procesamiento inmediato en Helena).
        """
        url = f"{self._base_url}/calls/bulk"
        params: dict[str, str] = {}
        if scheduled_date:
            params["scheduledDate"] = scheduled_date
        if scheduled_time:
            params["scheduledTime"] = scheduled_time

        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds * 3) as client:
            resp = await client.post(
                url,
                json=payload,
                headers=self._headers(content_type="json"),
                params=params or None,
            )
        resp.raise_for_status()
        return resp.json()

    async def send_unique(
        self,
        payload: dict[str, Any],
        scheduled_date: str = "",
        scheduled_time: str = "",
    ) -> dict[str, Any]:
        """Envía una llamada individual (`POST /calls`). Útil para pruebas."""
        url = f"{self._base_url}/calls"
        body = dict(payload)
        if scheduled_date:
            body["scheduledDate"] = scheduled_date
        if scheduled_time:
            body["scheduledTime"] = scheduled_time

        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds) as client:
            resp = await client.post(
                url, json=body, headers=self._headers(content_type="json")
            )
        resp.raise_for_status()
        return resp.json()

    # ── Cola (control de campañas en Helena; para fases futuras) ───────────────

    async def queue_status(
        self, organization_id: str | None = None, bulk_id: str | None = None
    ) -> dict[str, Any]:
        params: dict[str, str] = {}
        if organization_id:
            params["organizationId"] = organization_id
        if bulk_id:
            params["bulkId"] = bulk_id
        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds) as client:
            resp = await client.get(
                f"{self._base_url}/calls/queue/status",
                headers=self._headers(),
                params=params or None,
            )
        resp.raise_for_status()
        return resp.json()

    async def pause_queue(
        self,
        organization_id: str | None = None,
        bulk_id: str | None = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if organization_id:
            data["organizationId"] = organization_id
        if bulk_id:
            data["bulkId"] = bulk_id
        if reason:
            data["reason"] = reason
        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds) as client:
            resp = await client.patch(
                f"{self._base_url}/calls/queue/pause",
                headers=self._headers(content_type="json"),
                json=data,
            )
        resp.raise_for_status()
        return resp.json()

    async def resume_queue(
        self, organization_id: str | None = None, bulk_id: str | None = None
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if organization_id:
            data["organizationId"] = organization_id
        if bulk_id:
            data["bulkId"] = bulk_id
        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds) as client:
            resp = await client.patch(
                f"{self._base_url}/calls/queue/resume",
                headers=self._headers(content_type="json"),
                json=data,
            )
        resp.raise_for_status()
        return resp.json()

    async def cancel_queue(
        self,
        organization_id: str | None = None,
        bulk_id: str | None = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Cancela un bulk (`DELETE /calls/queue/cancel`). Irreversible en Helena.

        Se usa `client.request("DELETE", ...)` en vez de `client.delete(...)`
        porque este endpoint espera cuerpo JSON, y no todas las firmas de
        `.delete()` lo aceptan de forma consistente entre versiones de httpx.
        """
        data: dict[str, Any] = {}
        if organization_id:
            data["organizationId"] = organization_id
        if bulk_id:
            data["bulkId"] = bulk_id
        if reason:
            data["reason"] = reason
        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds) as client:
            resp = await client.request(
                "DELETE",
                f"{self._base_url}/calls/queue/cancel",
                headers=self._headers(content_type="json"),
                json=data,
            )
        resp.raise_for_status()
        return resp.json()

    async def set_allocation(
        self,
        bulk_id: str,
        calls_per_second: int | None = None,
        max_concurrent: int | None = None,
    ) -> dict[str, Any]:
        """Ajusta el ritmo de marcación de un bulk (`PATCH /calls/queue/allocation`)."""
        data: dict[str, Any] = {"bulkId": bulk_id}
        if calls_per_second is not None:
            data["callsPerSecond"] = calls_per_second
        if max_concurrent is not None:
            data["maxConcurrent"] = max_concurrent
        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds) as client:
            resp = await client.patch(
                f"{self._base_url}/calls/queue/allocation",
                headers=self._headers(content_type="json"),
                json=data,
            )
        resp.raise_for_status()
        return resp.json()

    async def get_allocation(self, bulk_id: str) -> dict[str, Any]:
        """Snapshot de ejecución de un bulk (`GET /calls/queue/allocation`)."""
        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds) as client:
            resp = await client.get(
                f"{self._base_url}/calls/queue/allocation",
                headers=self._headers(),
                params={"bulkId": bulk_id},
            )
        resp.raise_for_status()
        return resp.json()

    # ── Políticas de contacto (horarios permitidos de marcación) ───────────────

    async def list_contact_policies(self) -> Any:
        """Políticas de contacto de la organización (`GET /contact-policies`).

        Definen en qué franjas horarias se puede marcar (ventanas semanales,
        festivos del país y excepciones por fecha). En cobranza esto tiene
        implicación regulatoria, no solo operativa.
        """
        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds) as client:
            resp = await client.get(
                f"{self._base_url}/contact-policies", headers=self._headers()
            )
        resp.raise_for_status()
        return resp.json()

    # ── Webhooks (proxy /reporting -> helena-reporting) ────────────────────────

    async def register_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Registra un webhook (`POST /reporting/webhooks`).

        `payload`: `{url, events[], secret?, description?, metadata?}`. La
        organización se toma del propio token, no se envía.
        """
        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds) as client:
            resp = await client.post(
                f"{self._base_url}/reporting/webhooks",
                json=payload,
                headers=self._headers(content_type="json"),
            )
        resp.raise_for_status()
        return resp.json()

    async def list_webhooks(self) -> Any:
        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds) as client:
            resp = await client.get(
                f"{self._base_url}/reporting/webhooks", headers=self._headers()
            )
        resp.raise_for_status()
        return resp.json()

    async def update_webhook(
        self, webhook_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds) as client:
            resp = await client.patch(
                f"{self._base_url}/reporting/webhooks/{webhook_id}",
                json=payload,
                headers=self._headers(content_type="json"),
            )
        resp.raise_for_status()
        return resp.json()

    async def delete_webhook(self, webhook_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds) as client:
            resp = await client.delete(
                f"{self._base_url}/reporting/webhooks/{webhook_id}",
                headers=self._headers(content_type="json"),
            )
        resp.raise_for_status()
        return resp.json()

    async def test_webhook(self, webhook_id: str) -> dict[str, Any]:
        """Dispara un `TEST_EVENT` real contra la URL registrada."""
        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds) as client:
            resp = await client.post(
                f"{self._base_url}/reporting/webhooks/{webhook_id}/test",
                headers=self._headers(content_type="json"),
            )
        resp.raise_for_status()
        return resp.json()

    # ── Sounds (audios) ────────────────────────────────────────────────────────

    async def list_sounds(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds) as client:
            resp = await client.get(f"{self._base_url}/sounds", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    async def upload_sound(
        self,
        file_buffer: bytes,
        file_name: str,
        user_friendly_name: str | None = None,
        slot_number: str | None = None,
    ) -> dict[str, Any]:
        files = {"file": (file_name, file_buffer, "audio/wav")}
        data: dict[str, str] = {}
        if user_friendly_name:
            data["userFriendlyName"] = user_friendly_name
        if slot_number:
            data["slotNumber"] = slot_number
        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds * 2) as client:
            resp = await client.post(
                f"{self._base_url}/sounds/upload",
                files=files,
                data=data or None,
                headers=self._headers(),
            )
        resp.raise_for_status()
        return resp.json()

    async def delete_sound(self, audio_name: str) -> dict[str, Any]:
        name = audio_name if audio_name.endswith(".wav") else f"{audio_name}.wav"
        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds) as client:
            resp = await client.delete(
                f"{self._base_url}/sounds/{name}",
                headers=self._headers(content_type="json"),
            )
        resp.raise_for_status()
        return resp.json()

    async def fetch_sound(
        self, audio_name: str, range_header: str | None = None
    ) -> tuple[int, dict[str, str], bytes]:
        """Obtiene un audio desde Helena y devuelve (status, headers, contenido).

        Propaga el header `Range` para permitir seek en el reproductor del
        diseñador; devuelve el status de Helena (200 o 206) y los headers
        relevantes de streaming para reenviarlos tal cual.
        """
        extra = {"Range": range_header} if range_header else None
        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds) as client:
            resp = await client.get(
                f"{self._base_url}/sounds/audio/{audio_name}",
                headers=self._headers(extra=extra),
            )
        forwarded = {
            key: resp.headers[key]
            for key in (
                "content-type",
                "content-range",
                "accept-ranges",
                "content-length",
            )
            if key in resp.headers
        }
        return resp.status_code, forwarded, resp.content

    # ── Internos ────────────────────────────────────────────────────────────────

    def _headers(
        self,
        content_type: Literal["json"] | None = None,
        extra: dict[str, str] | None = None,
    ) -> dict[str, str]:
        headers: dict[str, str] = {"Authorization": f"Bearer {self._cfg.api_key}"}
        if content_type == "json":
            headers["Content-Type"] = "application/json"
        if extra:
            headers.update(extra)
        return headers
