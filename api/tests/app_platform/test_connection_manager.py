"""Unit tests puros (unittest.mock, sin DB ni WebSocket real) para
`ChatConnectionManager`: gestión de conexiones activas por usuario, límite de
conexiones simultáneas, y el broadcast/envío a conexiones muertas."""

import uuid
from unittest.mock import AsyncMock

import pytest

from app_platform.chats.websocket.connection_manager import ChatConnectionManager


def _fake_ws() -> AsyncMock:
    ws = AsyncMock()
    return ws


@pytest.fixture
def manager() -> ChatConnectionManager:
    return ChatConnectionManager()


class TestConnect:
    async def test_first_connection_is_accepted_and_tracked(
        self, manager: ChatConnectionManager
    ):
        user_id = uuid.uuid4()
        ws = _fake_ws()
        await manager.connect(user_id, ws)
        ws.accept.assert_awaited_once()
        assert user_id in manager.online_user_ids()

    async def test_multiple_connections_under_limit_are_all_kept(
        self, manager: ChatConnectionManager
    ):
        user_id = uuid.uuid4()
        ws1, ws2 = _fake_ws(), _fake_ws()
        await manager.connect(user_id, ws1)
        await manager.connect(user_id, ws2)
        assert manager._connections[user_id] == [ws1, ws2]

    async def test_exceeding_max_connections_closes_the_oldest(
        self, manager: ChatConnectionManager
    ):
        user_id = uuid.uuid4()
        sockets = [_fake_ws() for _ in range(4)]
        for ws in sockets:
            await manager.connect(user_id, ws)

        # El límite es 3: la primera conexión (la más vieja) debe cerrarse con 1008
        # y no seguir en la lista.
        sockets[0].close.assert_awaited_once_with(code=1008)
        assert sockets[0] not in manager._connections[user_id]
        assert manager._connections[user_id] == sockets[1:]
        assert len(manager._connections[user_id]) == 3

    async def test_close_failure_on_eviction_does_not_raise(
        self, manager: ChatConnectionManager
    ):
        user_id = uuid.uuid4()
        sockets = [_fake_ws() for _ in range(3)]
        sockets[0].close.side_effect = RuntimeError("already gone")
        for ws in sockets:
            await manager.connect(user_id, ws)
        # La 4ta conexión debe evictar a sockets[0] pese a que close() falle.
        new_ws = _fake_ws()
        await manager.connect(user_id, new_ws)
        assert len(manager._connections[user_id]) == 3


class TestDisconnect:
    async def test_removes_the_given_connection(self, manager: ChatConnectionManager):
        user_id = uuid.uuid4()
        ws = _fake_ws()
        await manager.connect(user_id, ws)
        manager.disconnect(user_id, ws)
        assert user_id not in manager.online_user_ids()

    async def test_disconnect_of_unknown_user_is_a_noop(
        self, manager: ChatConnectionManager
    ):
        manager.disconnect(uuid.uuid4(), _fake_ws())  # no debe lanzar

    async def test_disconnect_of_unknown_socket_for_known_user_is_a_noop(
        self, manager: ChatConnectionManager
    ):
        user_id = uuid.uuid4()
        await manager.connect(user_id, _fake_ws())
        manager.disconnect(user_id, _fake_ws())
        assert user_id in manager.online_user_ids()


class TestOnlineUserIds:
    async def test_only_users_with_active_connections_are_online(
        self, manager: ChatConnectionManager
    ):
        user_a, user_b = uuid.uuid4(), uuid.uuid4()
        ws_a = _fake_ws()
        await manager.connect(user_a, ws_a)
        await manager.connect(user_b, _fake_ws())
        manager.disconnect(user_b, manager._connections[user_b][0])
        assert manager.online_user_ids() == {user_a}


class TestSendToUser:
    async def test_sends_event_and_data_to_all_connections(
        self, manager: ChatConnectionManager
    ):
        user_id = uuid.uuid4()
        ws1, ws2 = _fake_ws(), _fake_ws()
        await manager.connect(user_id, ws1)
        await manager.connect(user_id, ws2)

        await manager.send_to_user(user_id, "message", {"body": "hola"})

        ws1.send_json.assert_awaited_once_with(
            {"event": "message", "data": {"body": "hola"}}
        )
        ws2.send_json.assert_awaited_once_with(
            {"event": "message", "data": {"body": "hola"}}
        )

    async def test_dead_connection_is_pruned_after_send_failure(
        self, manager: ChatConnectionManager
    ):
        user_id = uuid.uuid4()
        alive, dead = _fake_ws(), _fake_ws()
        dead.send_json.side_effect = RuntimeError("connection closed")
        await manager.connect(user_id, alive)
        await manager.connect(user_id, dead)

        await manager.send_to_user(user_id, "ping", {})

        assert dead not in manager._connections[user_id]
        assert alive in manager._connections[user_id]

    async def test_send_to_user_with_no_connections_is_a_noop(
        self, manager: ChatConnectionManager
    ):
        await manager.send_to_user(uuid.uuid4(), "ping", {})  # no debe lanzar


class TestBroadcastToOthers:
    async def test_excludes_the_given_user(self, manager: ChatConnectionManager):
        sender, other = uuid.uuid4(), uuid.uuid4()
        sender_ws, other_ws = _fake_ws(), _fake_ws()
        await manager.connect(sender, sender_ws)
        await manager.connect(other, other_ws)

        await manager.broadcast_to_others(sender, "typing", {"chatId": "x"})

        other_ws.send_json.assert_awaited_once_with(
            {"event": "typing", "data": {"chatId": "x"}}
        )
        sender_ws.send_json.assert_not_awaited()
