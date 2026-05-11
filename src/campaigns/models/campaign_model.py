from sqlalchemy import Column, Integer, String, UUID

from database.database import Base


class Campaign(Base):

    __tablename__ = "campanias"

    id = Column(UUID, primary_key=True, name="id", unique=True, nullable=False)

    name = Column(
        String, nullable=False, unique=True, index=True, name="nombre_campania"
    )

    description = Column(String, nullable=True, name="descripcion_campania")
