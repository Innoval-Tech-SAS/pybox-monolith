"""Schema de respuesta del estado de bloqueo por facturación de una organización."""

import uuid

from pydantic import Field

from billing.billing_status.enums.billing_status_enums import TenantBillingLockStatus
from core.base.schema_base import BaseSchema


class TenantBillingStatusResponse(BaseSchema):
    lock_status: TenantBillingLockStatus = Field(
        description="Nivel de bloqueo de la organizacion"
    )
    active_invoice_id: uuid.UUID | None = Field(
        default=None, description="Factura abierta que origina el estado"
    )
    message: str | None = Field(
        default=None, description="Mensaje descriptivo del estado"
    )
