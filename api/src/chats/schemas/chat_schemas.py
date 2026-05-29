from datetime import datetime

from base.schema_base import BaseSchema



class MessageSchema(BaseSchema):
    id: str
    chat_id: str
    sender_id: int
    sender_name: str
    sender_avatar: str | None = None
    body: str
    created_at: datetime
    status: str = "sent"


class ChatSummarySchema(BaseSchema):
    id: str
    type: int
    title: str
    peer_id: int | None = None
    peer_avatar: str | None = None
    last_message: str | None = None
    last_message_at: datetime | None = None
    unread_count: int = 0


class MessagesPageSchema(BaseSchema):
    items: list[MessageSchema]
    next_cursor: str | None = None
