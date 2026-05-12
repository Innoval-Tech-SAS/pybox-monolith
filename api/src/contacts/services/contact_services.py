from werkzeug.datastructures import FileStorage
from sqlalchemy.exc import IntegrityError

from ..repositories.contact_repository import ContactRepository
from ..utils.contact_error_messages import duplicate_contact_message
from ..utils.contact_exceptions import DuplicateContactError
from ..utils.contact_file_parser import ContactFileParser


class ContactServices:

    def __init__(self):
        self.repository = ContactRepository()
        self.file_parser = ContactFileParser()

    def process_file(self, file: FileStorage, type_file: str):
        try:
            return self._process_file(file, type_file)
        except IntegrityError as error:
            raise DuplicateContactError(duplicate_contact_message(error)) from error

    def _process_file(self, file: FileStorage, type_file: str):
        batch_size = 1000
        total_saved = 0
        batch = []
        file_data = self.file_parser.parse(file, type_file)

        for contact_data in file_data.contacts:
            contact = self.repository.model_class(**contact_data)
            batch.append(contact)

            if len(batch) >= batch_size:
                saved_contacts = self.repository.add_many(batch)
                total_saved += len(saved_contacts)
                batch.clear()

        if batch:
            saved_contacts = self.repository.add_many(batch)
            total_saved += len(saved_contacts)

        return {
            "total_saved": total_saved,
            "total_skipped": file_data.total_skipped,
            "extra_info_columns": file_data.extra_info_columns,
        }
