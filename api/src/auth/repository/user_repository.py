from base.repository_base import RepositoryBase
from database.database import db
from ..models.user_model import UserModel


class UserRepository(RepositoryBase[UserModel]):
    def __init__(self):
        super().__init__(db, UserModel)

    def get_by_email(self, email: str):
        with self.db.get_session() as session:
            return session.query(self.model_class).filter_by(email=email).first()
