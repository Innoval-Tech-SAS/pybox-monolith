import uuid

from sqlalchemy import (
    Boolean,
    Column,
    func,
    UUID,
    String,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship


from database.database import Base
from auth.enums.auth_enums import AuthProvider
from organizations.models.organization_membership_model import (
    OrganizationMembershipModel,
)
from ..enums.user_enums import UserDocumentType


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

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        name="id",
        default=uuid.uuid4,
    )
    firstname = Column(String(255), nullable=False, name="nombre")
    lastname = Column(String(255), nullable=False, name="apellido")
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        name="correo_electronico",
    )
    hashed_password = Column(
        String(255),
        nullable=True,
        name="contrasena_hash",
    )
    phone_number = Column(
        String(20), unique=True, nullable=False, name="numero_telefono"
    )
    auth_provider = Column(
        ENUM(AuthProvider),
        nullable=False,
        default=AuthProvider.SELF,
        name="proveedor_autenticacion",
    )
    provider_user_id = Column(
        String(255),
        nullable=True,
        name="id_usuario_proveedor",
    )
    document_type = Column(
        ENUM(UserDocumentType),
        nullable=False,
        default=UserDocumentType.CC,
        name="tipo_documento",
    )
    document_number = Column(String(50), nullable=False, name="numero_documento")

    is_active_sessions = Column(
        Boolean,
        nullable=False,
        default=False,
        name="sesion_activa",
    )

    is_active = Column(Boolean, nullable=False, default=True, name="activo")

    created_at = Column(DateTime, name="fecha_creacion", default=func.now())

    updated_at = Column(
        DateTime,
        nullable=True,
        name="fecha_actualizacion",
        onupdate=func.now(),
    )

    memberships = relationship(
        OrganizationMembershipModel,
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @property
    def full_name(self):
        return f"{self.firstname.strip()} {self.lastname}"
