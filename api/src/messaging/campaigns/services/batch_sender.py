from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from core.config.logger import logger
from messaging.campaigns.constants import BATCH_SIZE, MAX_RETRIES, RETRY_BASE_MS
from messaging.campaigns.schemas.batch_schemas import BatchStats, SendInput
from messaging.contacts.enums.contact_enums import ContactStatus
from messaging.contacts.models.contact_model import ContactModel
from messaging.contacts.repositories.contact_repository import ContactRepository
from messaging.gateway import DeliveryGateway


class BatchSender:

    def __init__(self, gateway: DeliveryGateway, repo: ContactRepository) -> None:
        self._gateway = gateway
        self._repo = repo

    async def process_batch(self, inputs: list[SendInput], channel_name: str) -> BatchStats:
        if not inputs:
            return BatchStats()

        stats = BatchStats()
        unique_recipients: set[str] = set()
        ch = channel_name.upper()

        chunks = [inputs[i : i + BATCH_SIZE] for i in range(0, len(inputs), BATCH_SIZE)]

        for chunk in chunks:
            try:
                if ch == "EMAIL":
                    ok, fail = await self._send_email_chunk(chunk, channel_name)
                else:
                    ok, fail = await self._send_sms_chunk(chunk, channel_name)
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

    async def _send_with_retry(
        self,
        channel: str,
        to: list[str],
        message: str,
        **kwargs: Any,
    ) -> tuple[bool, str | None]:
        last_err: str | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                ok = await self._gateway.send(channel, to, message, **kwargs)
                if ok:
                    return True, None
                last_err = "provider returned false"
            except Exception as exc:
                last_err = str(exc)
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_BASE_MS * (2 ** (attempt - 1)) / 1000)
        return False, last_err

    async def _persist_contact(
        self,
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
        await self._repo.add(contact)

    async def _send_sms_chunk(
        self,
        chunk: list[SendInput],
        channel_name: str,
        sender: str = "Template",
    ) -> tuple[int, int]:
        to = [inp.recipient for inp in chunk]
        sub = [inp.sub[0] if inp.sub else {} for inp in chunk]
        message = chunk[0].content

        ok, err = await self._send_with_retry(channel_name, to, message, sender=sender, sub=sub)
        now = datetime.now(timezone.utc) if ok else None
        status = ContactStatus.SENT if ok else ContactStatus.FAILED

        for inp in chunk:
            await self._persist_contact(inp, status, None, err, now)

        return (len(chunk), 0) if ok else (0, len(chunk))

    async def _send_email_chunk(
        self,
        chunk: list[SendInput],
        channel_name: str,
    ) -> tuple[int, int]:
        success = 0
        failure = 0
        for inp in chunk:
            ok, err = await self._send_with_retry(
                channel_name,
                [inp.recipient],
                inp.content,
                subject=inp.subject or "",
                sub=inp.sub,
            )
            now = datetime.now(timezone.utc) if ok else None
            status = ContactStatus.SENT if ok else ContactStatus.FAILED
            await self._persist_contact(inp, status, None, err, now)
            if ok:
                success += 1
            else:
                failure += 1
        return success, failure
