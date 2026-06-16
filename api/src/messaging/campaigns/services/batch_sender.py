"""
Procesa envíos en lotes (chunks de 100) con reintentos y persistencia en ContactModel.
SMS: envío bulk por chunk. Email: envío individual.
"""
from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.config.logger import logger
from messaging.contacts.enums.contact_enums import ContactStatus
from messaging.contacts.models.contact_model import ContactModel
from messaging.contacts.repositories.contact_repository import ContactRepository
from messaging.gateway import DeliveryGateway

BATCH_SIZE = 100
MAX_RETRIES = 3
RETRY_BASE_MS = 300


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


async def _sleep_ms(ms: int) -> None:
    await asyncio.sleep(ms / 1000)


async def _send_with_retry(
    gateway: DeliveryGateway,
    channel: str,
    to: list[str],
    message: str,
    **kwargs: Any,
) -> tuple[bool, str | None]:
    last_err: str | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            ok = await gateway.send(channel, to, message, **kwargs)
            if ok:
                return True, None
            last_err = "provider returned false"
        except Exception as exc:
            last_err = str(exc)
        if attempt < MAX_RETRIES:
            await _sleep_ms(RETRY_BASE_MS * (2 ** (attempt - 1)))
    return False, last_err


async def _persist_contact(
    repo: ContactRepository,
    inp: SendInput,
    status: ContactStatus,
    provider_id: str | None,
    error: str | None,
    sent_at: datetime | None,
) -> None:
    contact = ContactModel(
        content=inp.content,
        recipient=inp.recipient,
        status=status,
        debtor_id=inp.debtor_id,
        debtor_document=inp.debtor_document,
        sent_at=sent_at,
        provider_id=provider_id,
        error=error,
        campaign_id=inp.campaign_id,
        organization_id=inp.organization_id,
        portfolio_id=inp.portfolio_id,
        snapshot_channel_id=inp.snapshot_channel_id,
        snapshot_currency=inp.snapshot_currency,
        snapshot_unit_price=inp.snapshot_unit_price,
    )
    await repo.add(contact)


async def _send_sms_chunk(
    chunk: list[SendInput],
    gateway: DeliveryGateway,
    repo: ContactRepository,
    channel_name: str,
    sender: str = "Template",
) -> tuple[int, int]:
    to = [inp.recipient for inp in chunk]
    sub = [inp.sub[0] if inp.sub else {} for inp in chunk]
    message = chunk[0].content

    ok, err = await _send_with_retry(gateway, channel_name, to, message, sender=sender, sub=sub)
    now = datetime.now(timezone.utc) if ok else None
    status = ContactStatus.SENT if ok else ContactStatus.FAILED

    for inp in chunk:
        await _persist_contact(repo, inp, status, None, err, now)

    return (len(chunk), 0) if ok else (0, len(chunk))


async def _send_email_chunk(
    chunk: list[SendInput],
    gateway: DeliveryGateway,
    repo: ContactRepository,
    channel_name: str,
) -> tuple[int, int]:
    success = 0
    failure = 0
    for inp in chunk:
        ok, err = await _send_with_retry(
            gateway,
            channel_name,
            [inp.recipient],
            inp.content,
            subject=inp.subject or "",
            sub=inp.sub,
        )
        now = datetime.now(timezone.utc) if ok else None
        status = ContactStatus.SENT if ok else ContactStatus.FAILED
        await _persist_contact(repo, inp, status, None, err, now)
        if ok:
            success += 1
        else:
            failure += 1
    return success, failure


async def process_batch(
    inputs: list[SendInput],
    channel_name: str,
    session: AsyncSession,
    gateway: DeliveryGateway,
) -> BatchStats:
    if not inputs:
        return BatchStats()

    repo = ContactRepository(session)
    stats = BatchStats()
    unique_recipients: set[str] = set()
    ch = channel_name.upper()

    chunks = [inputs[i : i + BATCH_SIZE] for i in range(0, len(inputs), BATCH_SIZE)]

    for chunk in chunks:
        try:
            if ch == "EMAIL":
                ok, fail = await _send_email_chunk(chunk, gateway, repo, channel_name)
            else:
                ok, fail = await _send_sms_chunk(chunk, gateway, repo, channel_name)
            stats.success_count += ok
            stats.failure_count += fail
            stats.total_sent += len(chunk)
            for inp in chunk:
                unique_recipients.add(inp.recipient)
        except Exception:
            logger.exception("[batch_sender] error en chunk campaña=%s", inputs[0].campaign_id)
            stats.failure_count += len(chunk)
            stats.total_sent += len(chunk)

    stats.unique_customers = len(unique_recipients)
    return stats
