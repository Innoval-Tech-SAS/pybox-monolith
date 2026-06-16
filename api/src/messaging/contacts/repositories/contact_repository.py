from sqlalchemy.ext.asyncio import AsyncSession

from core.base.repository_base import RepositoryBase
from ..models.contact_model import ContactModel


class ContactRepository(RepositoryBase[ContactModel]):
    model_class = ContactModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)
