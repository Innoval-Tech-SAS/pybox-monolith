from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.models.permission_model import PermissionModel
from security.permissions import (
    PORTFOLIO_READ, PORTFOLIO_CREATE, PORTFOLIO_UPDATE, PORTFOLIO_DELETE,
    PORTFOLIO_STATS_READ, PORTFOLIO_ACL_READ, PORTFOLIO_ACL_MANAGE,
    INGEST_CREATE, INGEST_UPDATE,
    CREDITS_READ, CREDITS_CREATE,
    PAYMENTS_READ, PAYMENTS_CREATE,
    PAYMENT_METHODS_READ, PAYMENT_METHODS_CREATE, PAYMENT_METHODS_UPDATE, PAYMENT_METHODS_DELETE,
    DEBTORS_READ, DEBTORS_CREATE,
    ADDRESSES_READ, ADDRESSES_CREATE,
    CONTACT_METHODS_READ, CONTACT_METHODS_CREATE,
    REPORTS_GENERATE, REPORTS_READ,
    DAILY_COUNTERS_READ, DAILY_COUNTERS_UPDATE, DAILY_COUNTERS_SYNC,
)

_PERMISSIONS: list[tuple[str, str]] = [
    (PORTFOLIO_READ,           "Leer portafolios"),
    (PORTFOLIO_CREATE,         "Crear portafolios"),
    (PORTFOLIO_UPDATE,         "Actualizar portafolios"),
    (PORTFOLIO_DELETE,         "Eliminar portafolios"),
    (PORTFOLIO_STATS_READ,     "Leer estadísticas de portafolios"),
    (PORTFOLIO_ACL_READ,       "Leer ACL de portafolios"),
    (PORTFOLIO_ACL_MANAGE,     "Gestionar ACL de portafolios"),
    (INGEST_CREATE,            "Crear ingesta"),
    (INGEST_UPDATE,            "Actualizar ingesta"),
    (CREDITS_READ,             "Leer créditos"),
    (CREDITS_CREATE,           "Crear créditos"),
    (PAYMENTS_READ,            "Leer pagos"),
    (PAYMENTS_CREATE,          "Crear pagos"),
    (PAYMENT_METHODS_READ,     "Leer métodos de pago"),
    (PAYMENT_METHODS_CREATE,   "Crear métodos de pago"),
    (PAYMENT_METHODS_UPDATE,   "Actualizar métodos de pago"),
    (PAYMENT_METHODS_DELETE,   "Eliminar métodos de pago"),
    (DEBTORS_READ,             "Leer deudores"),
    (DEBTORS_CREATE,           "Crear deudores"),
    (ADDRESSES_READ,           "Leer direcciones"),
    (ADDRESSES_CREATE,         "Crear direcciones"),
    (CONTACT_METHODS_READ,     "Leer métodos de contacto"),
    (CONTACT_METHODS_CREATE,   "Crear métodos de contacto"),
    (REPORTS_GENERATE,         "Generar reportes"),
    (REPORTS_READ,             "Leer reportes"),
    (DAILY_COUNTERS_READ,      "Leer contadores diarios"),
    (DAILY_COUNTERS_UPDATE,    "Actualizar contadores diarios"),
    (DAILY_COUNTERS_SYNC,      "Sincronizar contadores diarios"),
]


async def seed_permissions(session: AsyncSession) -> None:
    existing = set(
        row[0]
        for row in (await session.execute(select(PermissionModel.name))).all()
    )
    new_permissions = [
        PermissionModel(name=name, label=label)
        for name, label in _PERMISSIONS
        if name not in existing
    ]
    if new_permissions:
        session.add_all(new_permissions)
        await session.commit()
