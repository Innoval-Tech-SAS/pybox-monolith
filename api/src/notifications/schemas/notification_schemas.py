from datetime import datetime
from typing import Any

from pydantic import field_validator

from base.schema_base import BaseSchema


class NotificationSchema(BaseSchema):
    id: int
    title: str
    body: str
    category: str
    notif_type: str
    is_read: bool
    created_at: datetime
    link: str | None = None
    details: dict[str, Any] | None = None

    @field_validator("notif_type", mode="before")
    @classmethod
    def _default_type(cls, v: str | None) -> str:
        return v or "info"
