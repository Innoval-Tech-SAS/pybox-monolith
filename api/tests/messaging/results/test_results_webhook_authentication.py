"""`POST /results/webhook` (eventos de 360NRS) no puede aceptar eventos de cualquiera.

360NRS no firma las notificaciones, así que la URL registrada en su dashboard lleva un
token compartido (`?token=`, `NRS360_WEBHOOK_TOKEN`). Sin token válido no se procesa el
evento: quien conozca un id de envío podría cambiar el estado de entrega de un contacto
de cualquier organización.
"""

import pytest

from messaging.results.services.webhook_service import WebhookService

URL = "/api/v1/results/webhook"
FORM = {"id": "ext-123", "event": "DELIVERED"}


@pytest.fixture
def handled(monkeypatch):
    """Registra las llamadas a `handle_event` sin tocar la base."""
    calls: list[tuple[str, str]] = []

    async def _handle(self, message_id: str, event: str) -> None:
        calls.append((message_id, event))

    monkeypatch.setattr(WebhookService, "handle_event", _handle)
    return calls


class TestWebhookAuthentication:
    async def test_without_token_is_rejected(self, client, monkeypatch, handled):
        monkeypatch.setenv("NRS360_WEBHOOK_TOKEN", "secreto")

        resp = await client.post(URL, data=FORM)

        assert resp.status_code == 401
        assert handled == []

    async def test_wrong_token_is_rejected(self, client, monkeypatch, handled):
        monkeypatch.setenv("NRS360_WEBHOOK_TOKEN", "secreto")

        resp = await client.post(URL, params={"token": "otro"}, data=FORM)

        assert resp.status_code == 401
        assert handled == []

    async def test_rejects_everything_when_the_secret_is_not_configured(self, client, monkeypatch, handled):
        monkeypatch.delenv("NRS360_WEBHOOK_TOKEN", raising=False)

        resp = await client.post(URL, params={"token": "cualquiera"}, data=FORM)

        assert resp.status_code == 401
        assert handled == []

    async def test_valid_token_processes_the_event(self, client, monkeypatch, handled):
        monkeypatch.setenv("NRS360_WEBHOOK_TOKEN", "secreto")

        resp = await client.post(URL, params={"token": "secreto"}, data=FORM)

        assert resp.status_code == 200
        assert resp.json() == {"success": True}
        assert handled == [("ext-123", "DELIVERED")]

    async def test_valid_token_with_unknown_event_still_answers_200(self, client, monkeypatch):
        """Contrato de degradación: un evento desconocido no debe hacer fallar el webhook
        (360NRS podría desactivar el endpoint tras fallos repetidos)."""
        monkeypatch.setenv("NRS360_WEBHOOK_TOKEN", "secreto")

        resp = await client.post(URL, params={"token": "secreto"}, data={"id": "ext-1", "event": "NOPE"})

        assert resp.status_code == 200
