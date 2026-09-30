"""Schemas de gestión de usuarios: alta, permisos y catálogo de roles/permisos."""

import uuid

from pydantic import EmailStr, Field

from core.base.schema_base import BaseSchema
from identity.users.enums.user_enums import PermissionEffect, UserRole


class ManagedUserCreate(BaseSchema):
    firstname: str = Field(description="Nombre")
    lastname: str = Field(description="Apellido")
    email: EmailStr = Field(description="Correo electrónico")
    phone_number: str = Field(description="Número de teléfono")
    password: str = Field(description="Contraseña inicial")
    role: UserRole = Field(description="Rol del usuario dentro de la organización")


class GlobalAdminCreate(BaseSchema):
    firstname: str = Field(description="Nombre")
    lastname: str = Field(description="Apellido")
    email: EmailStr = Field(description="Correo electrónico")
    phone_number: str = Field(description="Número de teléfono")
    password: str = Field(description="Contraseña inicial")


class PermissionCatalogEntry(BaseSchema):
    name: str = Field(description="Identificador del permiso (ej: portfolio.clients)")
    label: str | None = Field(default=None, description="Etiqueta legible")
    description: str | None = Field(default=None, description="Descripción del permiso")


class ManagedUserResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID del usuario")
    full_name: str = Field(description="Nombre completo")
    email: str = Field(description="Correo electrónico")
    phone_number: str = Field(description="Número de teléfono")
    role: str = Field(description="Rol asignado")
    scope: str = Field(description="Ámbito del usuario (GLOBAL u ORGANIZATION)")


class PermissionAssignRequest(BaseSchema):
    name: str = Field(description="Nombre del permiso a asignar")
    effect: PermissionEffect = Field(description="Efecto: ALLOW o DENY")


class PermissionEntry(BaseSchema):
    name: str = Field(description="Nombre del permiso")
    effect: str = Field(description="Efecto aplicado")


class PermissionListResponse(BaseSchema):
    permissions: list[PermissionEntry] = Field(
        description="Lista de permisos del miembro"
    )


class PortfolioAccessEntry(BaseSchema):
    portfolio_id: uuid.UUID = Field(description="ID del portafolio")
    name: str = Field(description="Nombre del portafolio")
    has_access: bool = Field(description="Indica si el miembro tiene acceso")
