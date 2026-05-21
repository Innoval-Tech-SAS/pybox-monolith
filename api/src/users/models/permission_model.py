from sqlalchemy import Boolean, Column, Integer, SmallInteger, String

from database.database import Base


class PermissionModel(Base):
    __tablename__ = "permisos"

    id = Column(Integer, primary_key=True, autoincrement=True, name="id")
    name = Column(String(100), unique=True, nullable=False, name="nombre")
    label = Column(String(255), nullable=True, name="etiqueta")
    description = Column(String(500), nullable=True, name="descripcion")
    max_level_access = Column(SmallInteger, nullable=False, default=1, name="nivel_acceso_maximo")
    is_active = Column(Boolean, nullable=False, default=True, name="activo")
