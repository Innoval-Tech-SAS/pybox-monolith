from sqlalchemy import Boolean, Column, Integer, String, DateTime, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from database.database import Base
from auth.enums.auth_enums import AuthProvider
from organizations.models.organization_membership_model import OrganizationMembershipModel
from countries.enums.country_enums import Nationality, UserDocumentType


class UserModel(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        UniqueConstraint(
            "tipo_documento",
            "numero_documento",
            name="uq_usuarios_tipo_numero_documento",
        ),
        UniqueConstraint(
            "proveedor_autenticacion",
            "id_usuario_proveedor",
            name="uq_usuarios_proveedor_usuario",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, name="id")
    firstname = Column(String(255), nullable=False, name="nombre")
    lastname = Column(String(255), nullable=False, name="apellido")
    email = Column(String(255), unique=True, nullable=False, name="correo_electronico")
    hashed_password = Column(String(255), nullable=True, name="contrasena_hash")
    phone_number = Column(String(20), unique=True, nullable=True, name="numero_telefono")
    auth_provider = Column(
        ENUM(AuthProvider),
        nullable=False,
        default=AuthProvider.SELF,
        name="proveedor_autenticacion",
    )
    provider_user_id = Column(String(255), nullable=True, name="id_usuario_proveedor")
    nationality = Column(ENUM(Nationality), nullable=True, name="nacionalidad")
    document_type = Column(ENUM(UserDocumentType), nullable=True, name="tipo_documento")
    document_number = Column(String(50), nullable=True, name="numero_documento")
    is_active_sessions = Column(Boolean, nullable=False, default=False, name="sesion_activa")
    is_active = Column(Boolean, nullable=False, default=True, name="activo")
    created_at = Column(DateTime, name="fecha_creacion", default=func.now())
    updated_at = Column(DateTime, nullable=True, name="fecha_actualizacion", onupdate=func.now())

    memberships = relationship(
        OrganizationMembershipModel,
        foreign_keys="[OrganizationMembershipModel.user_id]",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    created_memberships = relationship(
        OrganizationMembershipModel,
        foreign_keys="[OrganizationMembershipModel.created_by]",
        back_populates="creator",
    )

    @property
    def full_name(self) -> str:
        return f"{self.firstname.strip()} {self.lastname}"
