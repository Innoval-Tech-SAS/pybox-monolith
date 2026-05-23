from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.enums.auth_enums import AuthProvider
from base.soft_delete_repository_base import SoftDeleteRepositoryBase
from countries.enums.country_enums import UserDocumentType
from ..models.user_model import UserModel


class UserRepository(SoftDeleteRepositoryBase[UserModel]):
    model_class = UserModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_email(self, email: str) -> UserModel | None:
        result = await self.session.execute(
            select(UserModel).where(
                UserModel.email == email,
                UserModel.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    async def get_by_provider_identity(
        self,
        auth_provider: AuthProvider,
        provider_user_id: str,
    ) -> UserModel | None:
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.auth_provider == auth_provider)
            .where(UserModel.provider_user_id == provider_user_id)
            .where(UserModel.deleted_at.is_(None))
        )
        return result.scalars().first()

    async def get_by_phone_number(self, phone_number: str) -> UserModel | None:
        result = await self.session.execute(
            select(UserModel).where(
                UserModel.phone_number == phone_number,
                UserModel.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    async def get_by_document(
        self,
        document_type: UserDocumentType,
        document_number_hash: str,
    ) -> UserModel | None:
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.document_type == document_type)
            .where(UserModel.document_number_hash == document_number_hash)
            .where(UserModel.deleted_at.is_(None))
        )
        return result.scalars().first()

