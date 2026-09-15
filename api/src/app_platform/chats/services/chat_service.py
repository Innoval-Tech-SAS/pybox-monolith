from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status

from app_platform.chats.enums.chat_enums import ChatType, MemberRole
from app_platform.chats.models.chat_member_model import ChatMemberModel
from app_platform.chats.models.message_model import MessageModel
from app_platform.chats.models.message_status_model import MessageStatusModel
from app_platform.chats.repository.chat_repository import ChatRepository
from app_platform.chats.repository.message_repository import MessageRepository
from app_platform.chats.schemas.chat_schemas import (
    ChatSummarySchema,
    MessageSchema,
    MessagesPageSchema,
)
from identity.users.models.user_model import UserModel
from identity.users.repository.user_repository import UserRepository


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
        self, user_a: uuid.UUID, user_b: uuid.UUID
    ) -> ChatSummarySchema:
        from app_platform.chats.models.chat_model import ChatModel

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

    async def get_user_chats(self, user_id: uuid.UUID) -> list[ChatSummarySchema]:
        chats = await self.chat_repo.get_user_chats(user_id)
        if not chats:
            return []

        chat_ids = [chat.id for chat in chats]
        members_by_chat = await self.chat_repo.get_active_members_for_chats(chat_ids)
        last_messages_by_chat = await self.msg_repo.get_last_messages_for_chats(chat_ids)
        unread_by_chat = await self.msg_repo.get_unread_counts_for_chats(chat_ids, user_id)

        peer_user_ids = {
            member.user_id
            for chat in chats
            if chat.type == ChatType.DIRECT
            for member in members_by_chat.get(chat.id, [])
            if member.user_id != user_id
        }
        peer_users = await self.user_repo.get_by_ids(list(peer_user_ids))

        return [
            self._build_summary_from_batches(
                chat, user_id, members_by_chat, last_messages_by_chat, unread_by_chat, peer_users
            )
            for chat in chats
        ]

    def _build_summary_from_batches(
        self,
        chat,
        user_id: uuid.UUID,
        members_by_chat: dict[uuid.UUID, list[ChatMemberModel]],
        last_messages_by_chat: dict[uuid.UUID, MessageModel],
        unread_by_chat: dict[uuid.UUID, int],
        peer_users: dict[uuid.UUID, UserModel],
    ) -> ChatSummarySchema:
        title = chat.title or ""
        peer_id = None
        peer_avatar = None

        if chat.type == ChatType.DIRECT:
            members = members_by_chat.get(chat.id, [])
            peer_member = next((m for m in members if m.user_id != user_id), None)
            peer_user = peer_users.get(peer_member.user_id) if peer_member else None
            if peer_user:
                title = peer_user.full_name
                peer_id = peer_user.id
                peer_avatar = peer_user.profile_photo_url

        last_msg = last_messages_by_chat.get(chat.id)
        unread = unread_by_chat.get(chat.id, 0)

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

    async def _build_summary(self, chat, user_id: uuid.UUID) -> ChatSummarySchema:
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

    async def assert_member(self, chat_id: uuid.UUID, user_id: uuid.UUID) -> None:
        member = await self.chat_repo.get_member(chat_id, user_id)
        if not member or member.left_at is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No eres miembro de este chat.",
            )

    async def send_message(
        self, chat_id: uuid.UUID, sender_id: uuid.UUID, body: str
    ) -> tuple[MessageSchema, list[uuid.UUID]]:
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
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
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

        sender_cache: dict[uuid.UUID, any] = {}
        items: list[MessageSchema] = []

        for msg in rows:
            if msg.sender_id not in sender_cache:
                sender_cache[msg.sender_id] = await self.user_repo.get_by_id(msg.sender_id)
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

        items.reverse()
        next_cursor = rows[-1].created_at.isoformat() if has_more else None
        return MessagesPageSchema(items=items, next_cursor=next_cursor)

    async def mark_read(
        self, chat_id: uuid.UUID, user_id: uuid.UUID, message_ids: list[uuid.UUID]
    ) -> list[uuid.UUID]:
        await self.assert_member(chat_id, user_id)
        now = datetime.now(timezone.utc)
        for msg_id in message_ids:
            await self.msg_repo.mark_read(msg_id, user_id, now)
        members = await self.chat_repo.get_active_members(chat_id)
        return [m.user_id for m in members if m.user_id != user_id]

    async def mark_all_read(
        self, chat_id: uuid.UUID, user_id: uuid.UUID
    ) -> tuple[list[uuid.UUID], list[uuid.UUID]]:
        await self.assert_member(chat_id, user_id)
        now = datetime.now(timezone.utc)
        unread_ids = await self.msg_repo.get_unread_message_ids(chat_id, user_id)
        await self.msg_repo.mark_all_read(chat_id, user_id, now)
        members = await self.chat_repo.get_active_members(chat_id)
        other_ids = [m.user_id for m in members if m.user_id != user_id]
        return other_ids, unread_ids
