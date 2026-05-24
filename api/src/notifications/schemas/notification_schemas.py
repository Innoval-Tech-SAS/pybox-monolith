from datetime import datetime

from base.schema_base import BaseSchema


class NotificationSchema(BaseSchema):
    id: int
    title: str
    body: str
    category: str
    is_read: bool
    created_at: datetime
    link: str | None = None
