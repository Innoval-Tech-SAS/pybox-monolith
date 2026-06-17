import uuid
from typing import Sequence

from messaging.contacts.models.contact_model import ContactModel
from messaging.contacts.repositories.contact_repository import ContactRepository
from messaging.contacts.schemas.contact_schemas import ContactResponse, ContactsByChannelGroup


class ContactService:

    def __init__(self, repo: ContactRepository) -> None:
        self._repo = repo

    async def get_by_debtor(
        self,
        debtor_id: uuid.UUID,
        organization_id: uuid.UUID,
        portfolio_id: uuid.UUID | None = None,
    ) -> list[ContactsByChannelGroup]:
        contacts = await self._repo.get_by_debtor(debtor_id, organization_id, portfolio_id)
        return self._group_by_channel(list(contacts))

    def _group_by_channel(self, contacts: list[ContactModel]) -> list[ContactsByChannelGroup]:
        buckets: dict[int | None, list[ContactModel]] = {}
        for c in contacts:
            buckets.setdefault(c.snapshot_channel_id, []).append(c)

        groups: list[ContactsByChannelGroup] = []
        for channel_id, items in sorted(buckets.items(), key=lambda kv: (kv[0] is None, kv[0])):
            channel_name = items[0].snapshot_currency or "UNKNOWN"
            groups.append(
                ContactsByChannelGroup(
                    channel_id=channel_id,
                    channel_name=channel_name,
                    total=len(items),
                    items=[ContactResponse.model_validate(c) for c in items],
                )
            )
        return groups
