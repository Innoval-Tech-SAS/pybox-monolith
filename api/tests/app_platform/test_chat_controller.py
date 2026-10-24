import asyncio

import pytest
from httpx_ws import WebSocketDisconnect, aconnect_ws

from core.security.constants.cookie_constants import ACCESS_TOKEN_COOKIE
from tests.factories import get_user_by_email, mark_mfa_verified, register_payload

AUTH_BASE = "/api/v1/auth"
WS_URL = "/api/v1/chats/ws"


def _cookie(token: str) -> dict[str, str]:
    """El WebSocket se autentica solo con la cookie de acceso (no acepta `?token=`)."""
    return {"Cookie": f"{ACCESS_TOKEN_COOKIE}={token}"}


async def _register_and_get_token(client, db_session) -> tuple[str, str]:
    """Registra un usuario real y devuelve (access_token, user_id) -- el WS de chats
    lee `get_ws_session` como función directa, no como dependencia de FastAPI, así
    que `auth_as` no lo intercepta: hace falta un JWT real."""
    payload = register_payload()
    resp = await client.post(f"{AUTH_BASE}/register/user", json=payload)
    assert resp.status_code == 201
    token = resp.cookies[ACCESS_TOKEN_COOKIE]
    user = await get_user_by_email(db_session, payload["email"])
    await mark_mfa_verified(user.id)
    return token, str(user.id)


class TestChatWebSocket:
    async def test_list_chats_valid_empty(self, client, db_session, ws_client):
        token, _user_id = await _register_and_get_token(client, db_session)
        async with (
            ws_client() as ac,
            aconnect_ws(WS_URL, client=ac, headers=_cookie(token)) as ws,
        ):
            await ws.send_json({"event": "list_chats", "data": {}})
            reply = await ws.receive_json()
            assert reply["event"] == "chats"
            assert reply["data"] == []

    async def test_connect_without_token_rejected(self, ws_client):
        async with ws_client() as ac:
            with pytest.raises(WebSocketDisconnect) as exc_info:
                async with aconnect_ws(WS_URL, client=ac):
                    pass
            assert exc_info.value.code == 1008

    async def test_token_in_the_query_string_is_rejected(
        self, client, db_session, ws_client
    ):
        token, _user_id = await _register_and_get_token(client, db_session)
        async with ws_client() as ac:
            with pytest.raises(WebSocketDisconnect) as exc_info:
                async with aconnect_ws(f"{WS_URL}?token={token}", client=ac):
                    pass
            assert exc_info.value.code == 1008

    async def test_connect_invalid_token_rejected(self, ws_client):
        async with ws_client() as ac:
            with pytest.raises(WebSocketDisconnect) as exc_info:
                async with aconnect_ws(
                    WS_URL, client=ac, headers=_cookie("not-a-real-jwt")
                ):
                    pass
            assert exc_info.value.code == 1008

    async def test_create_direct_chat_and_send_message(
        self, client, db_session, ws_client
    ):
        token_a, _user_a_id = await _register_and_get_token(client, db_session)
        client.cookies.clear()
        token_b, user_b_id = await _register_and_get_token(client, db_session)

        async with (
            ws_client() as ac,
            aconnect_ws(WS_URL, client=ac, headers=_cookie(token_a)) as ws,
        ):
            await ws.send_json(
                {"event": "create_direct_chat", "data": {"peerId": user_b_id}}
            )
            reply = await ws.receive_json()
            assert reply["event"] == "chat"
            chat_id = reply["data"]["id"]
            assert reply["data"]["peerId"] == user_b_id

            await ws.send_json(
                {"event": "send_message", "data": {"chatId": chat_id, "body": "Hola!"}}
            )
            msg_reply = await ws.receive_json()
            assert msg_reply["event"] == "message"
            assert msg_reply["data"]["body"] == "Hola!"

            await ws.send_json({"event": "list_messages", "data": {"chatId": chat_id}})
            page = await ws.receive_json()
            assert page["event"] == "messages"
            assert len(page["data"]["items"]) == 1

    async def test_send_message_delivers_to_peer_in_real_time(
        self, client, db_session, ws_client
    ):
        token_a, _user_a_id = await _register_and_get_token(client, db_session)
        client.cookies.clear()
        token_b, user_b_id = await _register_and_get_token(client, db_session)

        async with (
            ws_client() as ac_a,
            aconnect_ws(WS_URL, client=ac_a, headers=_cookie(token_a)) as ws_a,
        ):
            await ws_a.send_json(
                {"event": "create_direct_chat", "data": {"peerId": user_b_id}}
            )
            chat_reply = await ws_a.receive_json()
            chat_id = chat_reply["data"]["id"]

            async with (
                ws_client() as ac_b,
                aconnect_ws(WS_URL, client=ac_b, headers=_cookie(token_b)) as ws_b,
            ):
                await ws_a.send_json(
                    {
                        "event": "send_message",
                        "data": {"chatId": chat_id, "body": "En vivo"},
                    }
                )
                await ws_a.receive_json()  # eco de confirmación para el emisor

                pushed = await asyncio.wait_for(ws_b.receive_json(), timeout=5)
                assert pushed["event"] == "message"
                assert pushed["data"]["body"] == "En vivo"

    async def test_send_message_to_chat_not_a_member_of_returns_error_event(
        self, client, db_session, ws_client
    ):
        token_a, _user_a_id = await _register_and_get_token(client, db_session)
        client.cookies.clear()
        token_b, user_b_id = await _register_and_get_token(client, db_session)
        client.cookies.clear()
        token_c, _user_c_id = await _register_and_get_token(client, db_session)

        async with (
            ws_client() as ac_a,
            aconnect_ws(WS_URL, client=ac_a, headers=_cookie(token_a)) as ws_a,
        ):
            await ws_a.send_json(
                {"event": "create_direct_chat", "data": {"peerId": user_b_id}}
            )
            chat_id = (await ws_a.receive_json())["data"]["id"]

        async with (
            ws_client() as ac_c,
            aconnect_ws(WS_URL, client=ac_c, headers=_cookie(token_c)) as ws_c,
        ):
            await ws_c.send_json(
                {"event": "send_message", "data": {"chatId": chat_id, "body": "colado"}}
            )
            reply = await ws_c.receive_json()
            assert reply["event"] == "error"

    async def test_read_marks_messages_and_notifies_peer(
        self, client, db_session, ws_client
    ):
        token_a, _user_a_id = await _register_and_get_token(client, db_session)
        client.cookies.clear()
        token_b, user_b_id = await _register_and_get_token(client, db_session)

        async with (
            ws_client() as ac_a,
            aconnect_ws(WS_URL, client=ac_a, headers=_cookie(token_a)) as ws_a,
        ):
            await ws_a.send_json(
                {"event": "create_direct_chat", "data": {"peerId": user_b_id}}
            )
            chat_id = (await ws_a.receive_json())["data"]["id"]

            async with (
                ws_client() as ac_b,
                aconnect_ws(WS_URL, client=ac_b, headers=_cookie(token_b)) as ws_b,
            ):
                await ws_a.send_json(
                    {
                        "event": "send_message",
                        "data": {"chatId": chat_id, "body": "leeme"},
                    }
                )
                sent = await ws_a.receive_json()
                message_id = sent["data"]["id"]
                await asyncio.wait_for(
                    ws_b.receive_json(), timeout=5
                )  # push del mensaje a B

                await ws_b.send_json({"event": "read_all", "data": {"chatId": chat_id}})
                read_push = await asyncio.wait_for(ws_a.receive_json(), timeout=5)
                assert read_push["event"] == "read"
                assert message_id in read_push["data"]["messageIds"]
