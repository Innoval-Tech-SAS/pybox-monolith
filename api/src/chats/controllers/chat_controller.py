import json

from fastapi import HTTPException, Query, WebSocket, WebSocketDisconnect, status

from chats.dependencies import ChatServiceDep
from chats.schemas.chat_schemas import (
    DirectChatRequest,
    MarkReadRequest,
    MessagesPageSchema,
    MessageSchema,
    ChatSummarySchema,
    SendMessageRequest,
)
from chats.websocket.connection_manager import ws_manager
from config.api_router import APIRouter
from database.redis import redis_client
from security.services.auth_token_service import AuthTokenService
from users.schemas.user_session_schema import UserSession, session_key
from security.dependencies import CurrentSession

router = APIRouter(prefix="/chats", tags=["chats"])

_ws_auth = AuthTokenService()


async def _authenticate_ws(token: str) -> UserSession:
    try:
        payload = _ws_auth.verify_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_id = int(payload["sub"])
    session = await redis_client.get_json(session_key(user_id), UserSession)
    if session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return session


@router.get("", response_model=list[ChatSummarySchema])
async def list_chats(session: CurrentSession, service: ChatServiceDep):
    return await service.get_user_chats(session.user_id)


@router.post("/direct", response_model=ChatSummarySchema)
async def create_direct_chat(
    body: DirectChatRequest, session: CurrentSession, service: ChatServiceDep
):
    return await service.find_or_create_direct_chat(session.user_id, body.peer_id)


@router.get("/{chat_id}/messages", response_model=MessagesPageSchema)
async def list_messages(
    chat_id: str,
    session: CurrentSession,
    service: ChatServiceDep,
    before: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
):
    return await service.list_messages(chat_id, session.user_id, before, limit)


@router.post("/{chat_id}/messages", response_model=MessageSchema)
async def send_message(
    chat_id: str,
    body: SendMessageRequest,
    session: CurrentSession,
    service: ChatServiceDep,
):
    msg_schema, recipient_ids = await service.send_message(
        chat_id, session.user_id, body.body
    )
    msg_data = json.loads(msg_schema.model_dump_json(by_alias=True))
    for uid in recipient_ids:
        await ws_manager.send_to_user(uid, "message", msg_data)
    return msg_schema


@router.post("/{chat_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_read(
    chat_id: str,
    body: MarkReadRequest,
    session: CurrentSession,
    service: ChatServiceDep,
):
    other_member_ids = await service.mark_read(
        chat_id, session.user_id, body.message_ids
    )
    read_data = {
        "chatId": chat_id,
        "messageIds": body.message_ids,
        "readerId": session.user_id,
    }
    for uid in other_member_ids:
        await ws_manager.send_to_user(uid, "read", read_data)


@router.websocket("/ws")
async def chat_ws(ws: WebSocket, token: str = Query(...)):
    try:
        session = await _authenticate_ws(token)
    except HTTPException:
        await ws.close(code=1008)
        return

    await ws_manager.connect(session.user_id, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(session.user_id, ws)
