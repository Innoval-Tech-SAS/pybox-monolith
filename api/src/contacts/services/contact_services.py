from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.contact_repository import ContactRepository
from ..utils.contact_error_messages import duplicate_contact_message
from ..utils.contact_exceptions import DuplicateContactError
from ..utils.contact_file_parser import ContactFileParser


class ContactServices:

    def __init__(self, session: AsyncSession):
        self.repository = ContactRepository(session)
        self.file_parser = ContactFileParser()

    async def process_file(self, file_bytes: bytes, type_file: str) -> dict:
        try:
            return await self._process_file(file_bytes, type_file)
        except IntegrityError as error:
            raise DuplicateContactError(duplicate_contact_message(error)) from error

    async def _process_file(self, file_bytes: bytes, type_file: str) -> dict:
        batch_size = 1000
        total_saved = 0
        batch = []
        file_data = self.file_parser.parse(file_bytes, type_file)

        for contact_data in file_data.contacts:
            contact = self.repository.model_class(**contact_data)
            batch.append(contact)

            if len(batch) >= batch_size:
                saved = await self.repository.add_many(batch)
                total_saved += len(saved)
                batch.clear()

        if batch:
            saved = await self.repository.add_many(batch)
            total_saved += len(saved)

        return {
            "total_saved": total_saved,
            "total_skipped": file_data.total_skipped,
            "extra_info_columns": file_data.extra_info_columns,
        }
