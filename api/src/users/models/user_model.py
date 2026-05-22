from datetime import datetime

from sqlalchemy import Boolean, Integer, String, DateTime, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, name="id")
    firstname: Mapped[str] = mapped_column(String(255), nullable=False, name="nombre")
    lastname: Mapped[str] = mapped_column(String(255), nullable=False, name="apellido")
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, name="correo_electronico")
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True, name="contrasena_hash")
    phone_number: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True, name="numero_telefono")
    auth_provider: Mapped[AuthProvider] = mapped_column(ENUM(AuthProvider), nullable=False, default=AuthProvider.SELF, name="proveedor_autenticacion")
    provider_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True, name="id_usuario_proveedor")
    nationality: Mapped[Nationality | None] = mapped_column(ENUM(Nationality), nullable=True, name="nacionalidad")
    document_type: Mapped[UserDocumentType | None] = mapped_column(ENUM(UserDocumentType), nullable=True, name="tipo_documento")
    document_number: Mapped[str | None] = mapped_column(String(50), nullable=True, name="numero_documento")
    is_email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, name="correo_verificado")
    is_phone_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, name="telefono_verificado")
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, name="mfa_habilitado")
    is_active_sessions: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, name="sesion_activa")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, name="activo")
    created_at: Mapped[datetime | None] = mapped_column(DateTime, name="fecha_creacion", default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, name="fecha_actualizacion", onupdate=func.now())

    memberships: Mapped[list[OrganizationMembershipModel]] = relationship(
        OrganizationMembershipModel,
        foreign_keys="[OrganizationMembershipModel.user_id]",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    created_memberships: Mapped[list[OrganizationMembershipModel]] = relationship(
        OrganizationMembershipModel,
        foreign_keys="[OrganizationMembershipModel.created_by]",
        back_populates="creator",
    )

    @property
    def full_name(self) -> str:
        return f"{self.firstname.strip()} {self.lastname}"
