"""Tests del envío en lote de campañas (ver batch_sender.py). Los tres riesgos que
cubre: (1) que un INSERT inválido al persistir un contacto tumbe el resto del chunk
por compartir transacción -- de ahí el savepoint de `add_isolated`; (2) que el
reintento ante fallas transitorias del proveedor no golpee con backoff creciente
(martillar al proveedor caído en vez de darle tiempo); (3) que una excepción en un
chunk complete detenga los chunks siguientes -- perdiendo envíos que sí podían
salir.

Unitarios puros: `MessageDispatcher` y `ContactRepository` van mockeados, nunca se
toca la base de datos ni un proveedor real.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from messaging.campaigns.constants import BATCH_SIZE, RETRY_BASE_MS
from messaging.campaigns.schemas.batch_schemas import SendInput
from messaging.campaigns.services.batch_sender import BatchSender
from messaging.channels.enums.channel_enums import ChannelName
from messaging.contacts.enums.contact_enums import ContactStatus


def make_send_input(**overrides) -> SendInput:
    defaults = dict(
        recipient=f"+57300{uuid.uuid4().int % 10**7:07d}",
        content="hola {nombre}, tienes una cuota pendiente",
        subject=None,
        debtor_id=uuid.uuid4(),
        debtor_document="123456789",
        campaign_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        portfolio_id=uuid.uuid4(),
        snapshot_channel_id=uuid.uuid4(),
        snapshot_currency="COP",
        snapshot_unit_price=None,
        sub=None,
    )
    defaults.update(overrides)
    return SendInput(**defaults)


class TestAddIsolatedFailureMidChunk:
    async def test_exception_persisting_one_contact_does_not_abort_rest_of_chunk(self):
        dispatcher = MagicMock()
        sender = MagicMock(sends_per_recipient=True)
        dispatcher.get_sender.return_value = sender
        dispatcher.send = AsyncMock(return_value=(True, {}, "sending-1"))

        repo = MagicMock()
        # La 2a llamada explota (p. ej. dato demasiado largo); 1a y 3a deben seguir
        # ejecutándose -- ese es justo el propósito del savepoint por contacto.
        repo.add_isolated = AsyncMock(side_effect=[None, RuntimeError("valor demasiado largo"), None])

        batch_sender = BatchSender(dispatcher, repo)
        inputs = [make_send_input() for _ in range(3)]

        stats = await batch_sender.process_batch(inputs, ChannelName.SMS)

        assert repo.add_isolated.call_count == 3
        # El fallo es solo al persistir el registro, no al envío en sí -- los 3 se
        # enviaron correctamente.
        assert stats.success_count == 3
        assert stats.failure_count == 0


class TestSendWithRetryBackoff:
    async def test_retries_use_increasing_backoff_before_succeeding(self):
        dispatcher = MagicMock()
        dispatcher.send = AsyncMock(
            side_effect=[
                Exception("timeout proveedor"),
                Exception("timeout proveedor"),
                (True, {"+573001112233": "ext-1"}, "sending-1"),
            ]
        )
        repo = MagicMock()
        batch_sender = BatchSender(dispatcher, repo)

        with patch(
            "messaging.campaigns.services.batch_sender.asyncio.sleep", new_callable=AsyncMock
        ) as mock_sleep:
            ok, err, ids_by_recipient, sending_id = await batch_sender._send_with_retry(
                ChannelName.SMS, ["+573001112233"], "hola"
            )

        assert ok is True
        assert err is None
        assert sending_id == "sending-1"

        # 2 reintentos entre los 3 intentos (el 3ro tiene éxito, no duerme después).
        assert mock_sleep.call_count == 2
        waited = [call.args[0] for call in mock_sleep.await_args_list]
        # Backoff exponencial (RETRY_BASE_MS * 2**(intento-1)): 0.3s, luego 0.6s -- no
        # son iguales entre sí (lineal/fijo) y crecen en ese orden.
        assert waited[0] == RETRY_BASE_MS * (2**0) / 1000
        assert waited[1] == RETRY_BASE_MS * (2**1) / 1000
        assert waited[0] < waited[1]


class TestSendChunkPhoneNormalization:
    async def test_phone_prefix_is_prepended_for_phone_channel(self):
        dispatcher = MagicMock()
        sender = MagicMock(sends_per_recipient=True)
        dispatcher.get_sender.return_value = sender
        dispatcher.send = AsyncMock(return_value=(True, {}, "sending-1"))
        repo = MagicMock()
        repo.add_isolated = AsyncMock()

        batch_sender = BatchSender(dispatcher, repo)
        chunk = [make_send_input(recipient="3001234567")]

        await batch_sender._send_chunk(chunk, ChannelName.SMS, sender.sends_per_recipient, phone_prefix="57")

        assert chunk[0].recipient == "573001234567"

    async def test_phone_prefix_is_not_applied_for_non_phone_channel(self):
        dispatcher = MagicMock()
        sender = MagicMock(sends_per_recipient=True)
        dispatcher.get_sender.return_value = sender
        dispatcher.send = AsyncMock(return_value=(True, {}, "sending-1"))
        repo = MagicMock()
        repo.add_isolated = AsyncMock()

        batch_sender = BatchSender(dispatcher, repo)
        chunk = [make_send_input(recipient="cliente@example.com")]

        await batch_sender._send_chunk(chunk, ChannelName.EMAIL, sender.sends_per_recipient, phone_prefix="57")

        assert chunk[0].recipient == "cliente@example.com"


class TestProcessBatchChunkExceptionIsolation:
    async def test_exception_in_one_chunk_does_not_stop_next_chunk(self):
        dispatcher = MagicMock()
        sender = MagicMock(sends_per_recipient=False)
        dispatcher.get_sender.return_value = sender
        repo = MagicMock()

        batch_sender = BatchSender(dispatcher, repo)
        # BATCH_SIZE items forman el primer chunk completo; 5 más arman un segundo chunk.
        campaign_id = uuid.uuid4()
        first_chunk_inputs = [make_send_input(campaign_id=campaign_id) for _ in range(BATCH_SIZE)]
        second_chunk_inputs = [make_send_input(campaign_id=campaign_id) for _ in range(5)]
        inputs = first_chunk_inputs + second_chunk_inputs

        # El primer chunk revienta con una excepción no controlada; el segundo debe
        # procesarse igual (no debe detener el resto del envío).
        batch_sender._send_chunk = AsyncMock(side_effect=[RuntimeError("chunk roto"), (5, 0)])

        stats = await batch_sender.process_batch(inputs, ChannelName.SMS)

        assert batch_sender._send_chunk.call_count == 2
        assert stats.failure_count == BATCH_SIZE
        assert stats.success_count == 5
        assert stats.total_sent == BATCH_SIZE + 5


class TestPersistContactsBulk:
    """Fase 5 de la auditoría: `_send_bulk` pasó de 1 `add_isolated` (INSERT con
    savepoint propio) POR destinatario a un solo `add_many_isolated` (un INSERT
    multi-fila, ver RepositoryBase) para todo el chunk, con fallback fila-por-fila
    (`add_isolated`, el camino viejo) solo si ese insert falla. Estos tests
    reemplazan el baseline de "N llamadas" que capturaba el comportamiento de ANTES
    de este refactor -- ya no aplica, el camino cambió a propósito."""

    async def test_send_bulk_persists_via_a_single_call(self):
        dispatcher = MagicMock()
        dispatcher.send = AsyncMock(return_value=(True, {}, "sending-1"))
        repo = MagicMock()
        repo.add_many_isolated = AsyncMock()
        repo.add_isolated = AsyncMock()

        batch_sender = BatchSender(dispatcher, repo)
        chunk = [make_send_input() for _ in range(10)]

        ok_count, fail_count = await batch_sender._send_bulk(chunk, ChannelName.SMS)

        assert ok_count == 10
        assert fail_count == 0
        assert repo.add_many_isolated.call_count == 1  # 1 llamada bulk, no 10 add_isolated
        repo.add_isolated.assert_not_called()

    async def test_send_bulk_persisted_content_matches_provider_result_per_recipient(self):
        dispatcher = MagicMock()
        repo = MagicMock()
        repo.add_many_isolated = AsyncMock()

        batch_sender = BatchSender(dispatcher, repo)
        chunk = [make_send_input() for _ in range(3)]
        recipients = [inp.recipient for inp in chunk]
        dispatcher.send = AsyncMock(
            return_value=(True, {r: f"ext-{i}" for i, r in enumerate(recipients)}, "sending-shared")
        )

        await batch_sender._send_bulk(chunk, ChannelName.SMS)

        contacts = repo.add_many_isolated.await_args.args[0]
        for i, contact in enumerate(contacts):
            assert contact.recipient == recipients[i]
            assert contact.status == ContactStatus.SENT
            assert contact.external_id == f"ext-{i}"
            assert contact.sending_id == "sending-shared"

    async def test_send_bulk_falls_back_to_add_isolated_when_bulk_insert_fails(self):
        """El INSERT multi-fila falla (p. ej. un dato demasiado largo en una sola fila
        del chunk) -> cae al camino viejo, fila por fila, SOLO para este chunk. Nunca
        se pierde la garantía de que un contacto inválido no tumbe el resto del envío."""
        dispatcher = MagicMock()
        dispatcher.send = AsyncMock(return_value=(True, {}, "sending-1"))
        repo = MagicMock()
        repo.add_many_isolated = AsyncMock(side_effect=RuntimeError("valor demasiado largo"))
        repo.add_isolated = AsyncMock()

        batch_sender = BatchSender(dispatcher, repo)
        chunk = [make_send_input() for _ in range(3)]

        ok_count, fail_count = await batch_sender._send_bulk(chunk, ChannelName.SMS)

        # El envío en sí ya se hizo con éxito (dispatcher.send) antes de intentar
        # persistir -- que el INSERT falle no debe revertir ok_count/fail_count.
        assert ok_count == 3
        assert fail_count == 0
        assert repo.add_isolated.call_count == 3  # fallback: 1 por destinatario
