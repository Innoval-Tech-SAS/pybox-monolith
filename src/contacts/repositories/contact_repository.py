from ..models.contact_model import ContactModel
from base.repository_base import RepositoryBase
from database.database import db


class ContactRepository(RepositoryBase[ContactModel]):

    def __init__(self):
        super().__init__(db, ContactModel)
