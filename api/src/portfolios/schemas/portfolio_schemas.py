import uuid
from datetime import date, datetime

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


class PortfolioUpdateRequest(BaseSchema):
    name: str | None = None
    description: str | None = None
    country: Nationality | None = None
    is_active: bool | None = None


class PortfolioStatsResponse(BaseSchema):
    creditos: int
    titulares: int
    codeudores: int
    clientes_unicos: int


class PortfolioAccessEntry(BaseSchema):
    user_id: int
    portfolio_id: uuid.UUID
    is_active: bool
    granted_at: datetime
    granted_by: int | None = None
    revoked_at: datetime | None = None


class PortfolioAccessReplaceRequest(BaseSchema):
    user_ids: list[int]


class PortfolioDailyCounterConfigResponse(BaseSchema):
    portfolio_id: uuid.UUID
    enabled: bool
    reactivation_mode: str
    updated_by: int | None = None
    last_synced_at: datetime | None = None
    last_synced_cutoff_date: date | None = None


class PortfolioDailyCounterConfigUpdateRequest(BaseSchema):
    enabled: bool | None = None
    reactivation_mode: str | None = None
