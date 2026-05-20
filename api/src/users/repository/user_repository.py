from base.repository_base import RepositoryBase
from auth.enums.auth_enums import AuthProvider
from database.database import db
from users.enums.user_enums import UserDocumentType
from ..models.user_model import UserModel


class UserRepository(RepositoryBase[UserModel]):
    def __init__(self):
        super().__init__(db, UserModel)

    def get_by_email(self, email: str) -> UserModel | None:
        with self.db.get_session() as session:
            return session.query(self.model_class).filter_by(email=email).first()

    def get_by_provider_identity(
        self,
        auth_provider: AuthProvider,
        provider_user_id: str,
    ) -> UserModel | None:
        with self.db.get_session() as session:
            return (
                session.query(self.model_class)
                .filter_by(
                    auth_provider=auth_provider,
                    provider_user_id=provider_user_id,
                )
                .first()
            )

    def get_by_phone_number(self, phone_number: str) -> UserModel | None:
        with self.db.get_session() as session:
            return (
                session.query(self.model_class)
                .filter_by(phone_number=phone_number)
                .first()
            )

    def get_by_document(
        self,
        document_type: UserDocumentType,
        document_number: str,
    ) -> UserModel | None:
        with self.db.get_session() as session:
            return (
                session.query(self.model_class)
                .filter_by(
                    document_type=document_type,
                    document_number=document_number,
                )
                .first()
            )
