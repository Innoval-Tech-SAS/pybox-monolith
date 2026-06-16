import json

from fastapi import Query, WebSocket, WebSocketDisconnect

from chats.dependencies import ChatServiceDep
from chats.websocket.connection_manager import ws_manager
from config.api_router import APIRouter
from security.dependencies import get_ws_session

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.websocket("/ws")
async def chat_ws(ws: WebSocket, service: ChatServiceDep, token: str = Query(...)):
    try:
        session = await get_ws_session(token)
    except HTTPException:
        await ws.close(code=1008)
        return

    await ws_manager.connect(session.user_id, ws)
    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
                event = msg.get("event")
                data = msg.get("data", {})
            except (json.JSONDecodeError, AttributeError):
                continue

            try:
                req_id = data.get("requestId") if isinstance(data, dict) else None

                async def reply(out_event: str, out_data) -> None:
                    payload = {"event": out_event, "data": out_data}
                    if req_id:
                        payload["requestId"] = req_id
                    await ws.send_json(payload)

                if event == "list_chats":
                    chats = await service.get_user_chats(session.user_id)
                    await reply("chats", [json.loads(c.model_dump_json(by_alias=True)) for c in chats])

                elif event == "create_direct_chat":
                    peer_id: int | None = data.get("peerId")
                    if peer_id:
                        chat = await service.find_or_create_direct_chat(session.user_id, peer_id)
                        await reply("chat", json.loads(chat.model_dump_json(by_alias=True)))

                elif event == "list_messages":
                    chat_id: str | None = data.get("chatId")
                    if chat_id:
                        before = data.get("before")
                        limit = data.get("limit", 50)
                        page = await service.list_messages(chat_id, session.user_id, before, limit)
                        await reply("messages", json.loads(page.model_dump_json(by_alias=True)))

                elif event == "send_message":
                    chat_id = data.get("chatId")
                    body = data.get("body", "")
                    if chat_id:
                        msg_schema, recipient_ids = await service.send_message(chat_id, session.user_id, body)
                        msg_data = json.loads(msg_schema.model_dump_json(by_alias=True))
                        for uid in recipient_ids:
                            await ws_manager.send_to_user(uid, "message", msg_data)
                        await reply("message", msg_data)

                elif event == "read":
                    chat_id = data.get("chatId")
                    message_ids = data.get("messageIds", [])
                    if chat_id and message_ids:
                        other_ids = await service.mark_read(chat_id, session.user_id, message_ids)
                        read_data = {
                            "chatId": chat_id,
                            "messageIds": message_ids,
                            "readerId": session.user_id,
                        }
                        for uid in other_ids:
                            await ws_manager.send_to_user(uid, "read", read_data)

                elif event == "read_all":
                    chat_id = data.get("chatId")
                    if chat_id:
                        other_ids, msg_ids = await service.mark_all_read(chat_id, session.user_id)
                        if msg_ids:
                            read_data = {
                                "chatId": chat_id,
                                "messageIds": msg_ids,
                                "readerId": session.user_id,
                            }
                            for uid in other_ids:
                                await ws_manager.send_to_user(uid, "read", read_data)

            except HTTPException as e:
                await ws.send_json({"event": "error", "data": {"detail": e.detail}})

    except WebSocketDisconnect:
        ws_manager.disconnect(session.user_id, ws)
