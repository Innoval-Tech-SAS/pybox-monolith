from datetime import datetime

from pydantic import Field

from core.base.schema_base import BaseSchema


class MessageSchema(BaseSchema):
    id: str = Field(description="ID del mensaje")
    chat_id: str = Field(description="ID del chat al que pertenece")
    sender_id: int = Field(description="ID del usuario que envió el mensaje")
    sender_name: str = Field(description="Nombre del remitente")
    sender_avatar: str | None = Field(default=None, description="URL del avatar del remitente")
    body: str = Field(description="Contenido del mensaje")
    created_at: datetime = Field(description="Fecha y hora de envío")
    status: str = Field(default="sent", description="Estado del mensaje (sent, read)")


class ChatSummarySchema(BaseSchema):
    id: str = Field(description="ID del chat")
    type: int = Field(description="Tipo de chat (1=directo)")
    title: str = Field(description="Título o nombre del chat")
    peer_id: int | None = Field(default=None, description="ID del otro participante en chats directos")
    peer_avatar: str | None = Field(default=None, description="Avatar del otro participante")
    last_message: str | None = Field(default=None, description="Último mensaje enviado")
    last_message_at: datetime | None = Field(default=None, description="Fecha del último mensaje")
    unread_count: int = Field(default=0, description="Cantidad de mensajes no leídos")


class MessagesPageSchema(BaseSchema):
    items: list[MessageSchema] = Field(description="Mensajes de la página")
    next_cursor: str | None = Field(default=None, description="Cursor para paginación hacia atrás")
