import uuid
from sqlalchemy import (
    func,
    UUID,
    Column,
    String,
    DateTime,
)

from core.database.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firstname = Column(String(255), nullable=False)
    lastname = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    @property
    def full_name(self):
        return f"{self.firstname} {self.lastname}"
