from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status

from chats.enums.chat_enums import ChatType, MemberRole
from chats.models.chat_member_model import ChatMemberModel
from chats.models.message_model import MessageModel
from chats.models.message_status_model import MessageStatusModel
from chats.repository.chat_repository import ChatRepository
from chats.repository.message_repository import MessageRepository
from chats.schemas.chat_schemas import (
    ChatSummarySchema,
    MessageSchema,
    MessagesPageSchema,
)
from users.repository.user_repository import UserRepository


class ChatService:
    def __init__(
        self,
        chat_repo: ChatRepository,
        msg_repo: MessageRepository,
        user_repo: UserRepository,
    ):
        self.chat_repo = chat_repo
        self.msg_repo = msg_repo
        self.user_repo = user_repo

    async def find_or_create_direct_chat(
        self, user_a: int, user_b: int
    ) -> ChatSummarySchema:
        from chats.models.chat_model import ChatModel

        dm_key = ChatModel.build_dm_key(user_a, user_b)
        chat = await self.chat_repo.get_by_dm_key(dm_key)
        if not chat:
            chat = ChatModel(type=ChatType.DIRECT, dm_key=dm_key)
            chat = await self.chat_repo.add(chat)
            await self.chat_repo.add_member(
                ChatMemberModel(chat_id=chat.id, user_id=user_a, role=MemberRole.MEMBER)
            )
            await self.chat_repo.add_member(
                ChatMemberModel(chat_id=chat.id, user_id=user_b, role=MemberRole.MEMBER)
            )
        return await self._build_summary(chat, user_a)

    async def get_user_chats(self, user_id: int) -> list[ChatSummarySchema]:
        chats = await self.chat_repo.get_user_chats(user_id)
        summaries = []
        for chat in chats:
            summaries.append(await self._build_summary(chat, user_id))
        return summaries

    async def _build_summary(self, chat, user_id: int) -> ChatSummarySchema:
        title = chat.title or ""
        peer_id = None
        peer_avatar = None

        if chat.type == ChatType.DIRECT:
            members = await self.chat_repo.get_active_members(chat.id)
            peer_member = next((m for m in members if m.user_id != user_id), None)
            if peer_member:
                peer_user = await self.user_repo.get_by_id(peer_member.user_id)
                if peer_user:
                    title = peer_user.full_name
                    peer_id = peer_user.id
                    peer_avatar = peer_user.profile_photo_url

        last_msg = await self.msg_repo.get_last_message(chat.id)
        unread = await self.msg_repo.get_unread_count(chat.id, user_id)

        return ChatSummarySchema(
            id=chat.id,
            type=chat.type,
            title=title,
            peer_id=peer_id,
            peer_avatar=peer_avatar,
            last_message=last_msg.body if last_msg else None,
            last_message_at=last_msg.created_at if last_msg else None,
            unread_count=unread,
        )

    async def assert_member(self, chat_id: str, user_id: int) -> None:
        member = await self.chat_repo.get_member(chat_id, user_id)
        if not member or member.left_at is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No eres miembro de este chat.",
            )

    async def send_message(
        self, chat_id: str, sender_id: int, body: str
    ) -> tuple[MessageSchema, list[int]]:
        await self.assert_member(chat_id, sender_id)

        body = body.strip()
        if not body:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El mensaje no puede estar vacío.",
            )

        msg = MessageModel(chat_id=chat_id, sender_id=sender_id, body=body)
        msg = await self.msg_repo.add(msg)

        now = datetime.now(timezone.utc)
        members = await self.chat_repo.get_active_members(chat_id)
        member_ids = [m.user_id for m in members]

        statuses = [
            MessageStatusModel(
                message_id=msg.id,
                user_id=uid,
                delivered_at=now,
                read_at=now if uid == sender_id else None,
            )
            for uid in member_ids
        ]
        await self.msg_repo.add_statuses(statuses)

        sender = await self.user_repo.get_by_id(sender_id)
        msg_schema = MessageSchema(
            id=msg.id,
            chat_id=chat_id,
            sender_id=sender_id,
            sender_name=sender.full_name if sender else "Usuario",
            sender_avatar=sender.profile_photo_url if sender else None,
            body=msg.body,
            created_at=msg.created_at,
            status="sent",
        )
        other_ids = [uid for uid in member_ids if uid != sender_id]
        return msg_schema, other_ids

    async def list_messages(
        self,
        chat_id: str,
        user_id: int,
        before_ts: str | None,
        limit: int,
    ) -> MessagesPageSchema:
        await self.assert_member(chat_id, user_id)

        before_dt = datetime.fromisoformat(before_ts) if before_ts else None
        rows = await self.msg_repo.get_chat_messages(chat_id, before_dt, limit + 1)

        has_more = len(rows) > limit
        if has_more:
            rows = rows[:limit]

        if not rows:
            return MessagesPageSchema(items=[], next_cursor=None)

        statuses_map = await self.msg_repo.get_statuses_for_messages(
            [m.id for m in rows]
        )

        sender_cache: dict[int, any] = {}
        items: list[MessageSchema] = []

        for msg in rows:
            if msg.sender_id not in sender_cache:
                sender_cache[msg.sender_id] = await self.user_repo.get_by_id(
                    msg.sender_id
                )
            sender = sender_cache[msg.sender_id]

            msg_statuses = statuses_map.get(msg.id, [])
            other = [s for s in msg_statuses if s.user_id != msg.sender_id]
            if other and all(s.read_at for s in other):
                msg_status = "read"
            elif other and all(s.delivered_at for s in other):
                msg_status = "delivered"
            else:
                msg_status = "sent"

            items.append(
                MessageSchema(
                    id=msg.id,
                    chat_id=msg.chat_id,
                    sender_id=msg.sender_id,
                    sender_name=sender.full_name if sender else "Usuario",
                    sender_avatar=sender.profile_photo_url if sender else None,
                    body=msg.body,
                    created_at=msg.created_at,
                    status=msg_status,
                )
            )

        # Reverse to chronological order (oldest first)
        items.reverse()
        next_cursor = rows[-1].created_at.isoformat() if has_more else None

        return MessagesPageSchema(items=items, next_cursor=next_cursor)

    async def mark_read(
        self, chat_id: str, user_id: int, message_ids: list[str]
    ) -> list[int]:
        now = datetime.now(timezone.utc)
        for msg_id in message_ids:
            await self.msg_repo.mark_read(msg_id, user_id, now)
        members = await self.chat_repo.get_active_members(chat_id)
        return [m.user_id for m in members if m.user_id != user_id]
