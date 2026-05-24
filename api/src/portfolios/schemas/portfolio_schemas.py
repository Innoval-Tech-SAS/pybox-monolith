import uuid
from datetime import datetime

from base.schema_base import BaseSchema
from countries.enums.country_enums import Nationality


class PortfolioResponse(BaseSchema):
    id: uuid.UUID
    name: str
    description: str | None = None
    organization_id: uuid.UUID
    country: Nationality | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None
