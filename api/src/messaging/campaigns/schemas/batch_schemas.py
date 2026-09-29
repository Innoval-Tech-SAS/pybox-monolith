"""Estructuras internas de envío por lote (no expuestas en la API)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass
class SendInput:
    recipient: str
    content: str
    subject: str | None
    debtor_id: uuid.UUID | None
    debtor_document: str | None
    campaign_id: uuid.UUID
    organization_id: uuid.UUID
    portfolio_id: uuid.UUID | None
    snapshot_channel_id: uuid.UUID | None
    snapshot_currency: str | None
    snapshot_unit_price: Decimal | None
    sub: list[dict[str, Any]] | None = field(default=None)


@dataclass
class BatchStats:
    total_sent: int = 0
    success_count: int = 0
    failure_count: int = 0
    unique_customers: int = 0
