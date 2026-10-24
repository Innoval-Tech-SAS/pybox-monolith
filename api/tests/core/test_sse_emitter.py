import uuid

from core.sse.sse_emitter import SSEEmitter


class TestSSEEmitter:
    async def test_emit_without_subscribers_does_not_crash(self):
        emitter = SSEEmitter()
        # Nadie suscrito a este user_id: no debe lanzar ni bloquear.
        await emitter.emit(uuid.uuid4(), "notification", {"hello": "world"})

    async def test_subscribe_then_emit_delivers_to_queue(self):
        emitter = SSEEmitter()
        user_id = uuid.uuid4()
        queue = emitter.subscribe(user_id)

        await emitter.emit(user_id, "notification", {"count": 1})

        message = queue.get_nowait()
        assert message["event"] == "notification"
        assert message["data"] == '{"count": 1}'

    async def test_emit_delivers_to_all_subscribed_queues(self):
        emitter = SSEEmitter()
        user_id = uuid.uuid4()
        queue_a = emitter.subscribe(user_id)
        queue_b = emitter.subscribe(user_id)

        await emitter.emit(user_id, "ping", {})

        assert queue_a.get_nowait()["event"] == "ping"
        assert queue_b.get_nowait()["event"] == "ping"

    async def test_unsubscribe_stops_delivery_and_cleans_up_empty_entry(self):
        emitter = SSEEmitter()
        user_id = uuid.uuid4()
        queue = emitter.subscribe(user_id)

        emitter.unsubscribe(user_id, queue)

        assert user_id not in emitter._queues
        await emitter.emit(user_id, "ping", {})
        assert queue.empty()

    async def test_unsubscribe_unknown_queue_is_noop(self):
        emitter = SSEEmitter()
        user_id = uuid.uuid4()
        emitter.subscribe(user_id)
        other_queue = __import__("asyncio").Queue()

        # Una queue que nunca se suscribió no debe lanzar al desuscribirse.
        emitter.unsubscribe(user_id, other_queue)

    async def test_unsubscribe_one_of_many_keeps_the_rest(self):
        emitter = SSEEmitter()
        user_id = uuid.uuid4()
        queue_a = emitter.subscribe(user_id)
        queue_b = emitter.subscribe(user_id)

        emitter.unsubscribe(user_id, queue_a)
        await emitter.emit(user_id, "ping", {})

        assert queue_a.empty()
        assert queue_b.get_nowait()["event"] == "ping"
