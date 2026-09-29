import uuid
from datetime import date, datetime

from pydantic import Field

from app_platform.countries.enums.country_enums import Nationality
from core.base.schema_base import BaseSchema


class PortfolioResponse(BaseSchema):
    id: uuid.UUID = Field(description="ID del portafolio")
    name: str = Field(description="Nombre del portafolio")
    description: str | None = Field(default=None, description="Descripción")
    organization_id: uuid.UUID = Field(description="ID de la organización propietaria")
    country: Nationality | None = Field(default=None, description="País del portafolio")
    is_active: bool = Field(description="Indica si el portafolio está activo")
    created_at: datetime = Field(description="Fecha de creación")
    updated_at: datetime | None = Field(
        default=None, description="Fecha de última actualización"
    )


class PortfolioUpdateRequest(BaseSchema):
    name: str | None = Field(default=None, description="Nuevo nombre")
    description: str | None = Field(default=None, description="Nueva descripción")
    country: Nationality | None = Field(default=None, description="País")
    is_active: bool | None = Field(
        default=None, description="Activar o desactivar el portafolio"
    )


class PortfolioStatsResponse(BaseSchema):
    creditos: int = Field(description="Total de créditos en el portafolio")
    titulares: int = Field(description="Total de deudores titulares únicos")
    codeudores: int = Field(description="Total de co-deudores únicos")
    clientes_unicos: int = Field(
        description="Total de clientes únicos (titulares + co-deudores sin duplicados)"
    )
    total_mora: float = Field(
        description=(
            "Suma del saldo capital en mora de todos los créditos del portafolio"
        )
    )
    documentos_unicos: int = Field(
        description=(
            "Conteo de combinaciones únicas (tipo de documento + número de "
            "documento) entre titulares y co-deudores"
        )
    )
    creditos_cargados: int = Field(
        description="Conteo de créditos cargados en el portafolio"
    )
    usuarios_con_acceso: int = Field(
        description="Conteo de usuarios con acceso activo al portafolio"
    )


class PortfolioAccessEntry(BaseSchema):
    user_id: uuid.UUID = Field(description="ID del usuario")
    portfolio_id: uuid.UUID = Field(description="ID del portafolio")
    is_active: bool = Field(description="Indica si el acceso está activo")
    granted_at: datetime = Field(description="Fecha en que se concedió el acceso")
    granted_by: uuid.UUID | None = Field(
        default=None, description="ID del usuario que concedió el acceso"
    )
    revoked_at: datetime | None = Field(
        default=None, description="Fecha en que se revocó el acceso"
    )


class PortfolioAccessReplaceRequest(BaseSchema):
    user_ids: list[uuid.UUID] = Field(
        description="Lista de IDs de usuarios con acceso al portafolio"
    )


class PortfolioDailyCounterConfigResponse(BaseSchema):
    portfolio_id: uuid.UUID = Field(description="ID del portafolio")
    enabled: bool = Field(description="Indica si el contador diario está habilitado")
    reactivation_mode: str = Field(
        description="Modo de reactivación: FROM_TODAY u otro"
    )
    updated_by: uuid.UUID | None = Field(
        default=None, description="ID del usuario que actualizó la configuración"
    )
    last_synced_at: datetime | None = Field(
        default=None, description="Última sincronización"
    )
    last_synced_cutoff_date: date | None = Field(
        default=None, description="Fecha de corte de la última sincronización"
    )


class PortfolioDailyCounterConfigUpdateRequest(BaseSchema):
    enabled: bool | None = Field(
        default=None, description="Habilitar o deshabilitar el contador diario"
    )
    reactivation_mode: str | None = Field(
        default=None, description="Modo de reactivación"
    )


class PortfolioDailyCounterConfigSyncRequest(BaseSchema):
    target_date: date | None = Field(
        default=None,
        description="Fecha de corte a registrar; si se omite usa la fecha de hoy",
    )
