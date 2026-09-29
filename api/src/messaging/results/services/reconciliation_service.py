"""Reconciliación periódica de eventos de envío (SMS/email) contra 360NRS."""

from __future__ import annotations

import io
import uuid

import polars as pl
from sqlalchemy.ext.asyncio import AsyncSession

from core.config.logger import logger
from messaging.campaigns.repository.campaign_result_repository import (
    CampaignResultRepository,
)
from messaging.channels.enums.channel_enums import ChannelName
from messaging.contacts.enums.contact_enums import ContactStatus
from messaging.contacts.models.contact_model import ContactModel
from messaging.contacts.repository.contact_repository import ContactRepository
from messaging.providers.email_provider import NRS360EmailProvider
from messaging.providers.sms_provider import NRS360SmsProvider

_SUCCESS_STATUSES = {
    ContactStatus.DELIVERED,
    ContactStatus.OPENED,
    ContactStatus.CLICKED,
    ContactStatus.FORM_OPENED,
    ContactStatus.FORM_SUBMITTED,
}
_FAILURE_STATUSES = {
    ContactStatus.HARD_BOUNCED,
    ContactStatus.SOFT_BOUNCED,
    ContactStatus.UNDELIVERED,
    ContactStatus.REJECTED,
    ContactStatus.EXPIRED,
    ContactStatus.COMPLAINT,
    ContactStatus.FORM_REJECTED,
}


def make_reconciliation_service(session: AsyncSession) -> ReconciliationService:
    return ReconciliationService(
        contact_repo=ContactRepository(session),
        result_repo=CampaignResultRepository(session),
        sms_provider=NRS360SmsProvider(),
        email_provider=NRS360EmailProvider(),
    )


class ReconciliationService:
    def __init__(
        self,
        contact_repo: ContactRepository,
        result_repo: CampaignResultRepository,
        sms_provider: NRS360SmsProvider,
        email_provider: NRS360EmailProvider,
    ) -> None:
        self._contact_repo = contact_repo
        self._result_repo = result_repo
        self._sms_provider = sms_provider
        self._email_provider = email_provider

    async def run(self) -> int:
        pending = await self._contact_repo.get_pending_sending_ids()
        reconciled = 0
        for sending_id, channel_name in pending:
            try:
                if await self._reconcile_sending(sending_id, channel_name):
                    reconciled += 1
            except Exception:
                logger.exception(
                    "[results_reconciliation] error en sending_id=%s", sending_id
                )
        return reconciled

    async def _reconcile_sending(
        self, sending_id: str, channel_name: ChannelName
    ) -> bool:
        if channel_name == ChannelName.SMS:
            provider = self._sms_provider
        elif channel_name == ChannelName.EMAIL:
            provider = self._email_provider
        else:
            return False

        csv_text = await provider.get_sending_events_report(sending_id)
        if not csv_text.strip():
            return False

        last_events = self._last_event_per_recipient(csv_text)
        if last_events is None:
            return False

        contacts = await self._contact_repo.get_by_sending_id(sending_id)
        contacts_by_recipient = {c.recipient: c for c in contacts}

        changed: list[ContactModel] = []
        for recipient, event in last_events.items():
            contact = contacts_by_recipient.get(recipient)
            if contact is None:
                continue
            try:
                new_status = ContactStatus(event.upper())
            except ValueError:
                logger.warning(
                    "[results_reconciliation] evento desconocido=%s sending_id=%s",
                    event,
                    sending_id,
                )
                continue
            if contact.status == new_status:
                continue
            contact.status = new_status
            changed.append(contact)

        if not changed:
            return False

        # Los `contact` en `changed` ya salieron de la sesión activa
        # (get_by_sending_id): ya están dirty-tracked, no hace falta
        # merge()+refresh() por fila — un solo flush() emite todos los
        # UPDATE de esta reconciliación.
        await self._contact_repo.session.flush()

        await self._insert_campaign_result(sending_id, contacts)
        return True

    def _last_event_per_recipient(self, csv_text: str) -> dict[str, str] | None:
        df = pl.read_csv(io.BytesIO(csv_text.encode()))
        if df.is_empty():
            return None

        df = df.with_columns(
            pl.coalesce([pl.col("phone"), pl.col("email")]).alias("recipient")
        )
        df = df.filter(pl.col("recipient").is_not_null())
        last = df.sort("createdAt").unique(subset=["recipient"], keep="last")
        return dict(zip(last["recipient"].to_list(), last["event"].to_list()))

    async def _insert_campaign_result(
        self, sending_id: str, contacts: list[ContactModel]
    ) -> None:
        if not contacts:
            return

        campaign_id: uuid.UUID = contacts[0].campaign_id
        organization_id: uuid.UUID = contacts[0].organization_id

        success_count = sum(1 for c in contacts if c.status in _SUCCESS_STATUSES)
        failure_count = sum(1 for c in contacts if c.status in _FAILURE_STATUSES)
        unique_customers = len({c.recipient for c in contacts})

        await self._result_repo.create(
            campaign_id=campaign_id,
            organization_id=organization_id,
            campaign_time_id=None,
            total_sent=len(contacts),
            success_count=success_count,
            failure_count=failure_count,
            unique_customers=unique_customers,
            sending_id=sending_id,
        )
