"""Mapeo de rol -> conjunto de permisos base que ese rol otorga por defecto."""

from core.security.constants.permissions import (
    MANAGE_WHATSAPP_CHATS,
    ORG_BILLING,
    ORG_CAMPAIGNS,
    ORG_PAYMENT_METHODS,
    ORG_PORTFOLIOS,
    ORG_REPORTS,
    ORG_TEMPLATES,
    ORG_USERS,
    PORTFOLIO_CLIENTS,
    PORTFOLIO_COMMUNICATIONS,
    PORTFOLIO_JUDICIAL,
    PORTFOLIO_UPLOAD_NEW,
    PORTFOLIO_UPLOAD_UPDATE,
)
from identity.users.enums.user_enums import UserRole

ROLE_PERMISSIONS: dict[UserRole, frozenset[str]] = {
    UserRole.ADMIN: frozenset(
        {
            ORG_PORTFOLIOS,
            ORG_PAYMENT_METHODS,
            ORG_REPORTS,
            ORG_USERS,
            ORG_CAMPAIGNS,
            ORG_TEMPLATES,
            ORG_BILLING,
            PORTFOLIO_CLIENTS,
            PORTFOLIO_UPLOAD_NEW,
            PORTFOLIO_UPLOAD_UPDATE,
            PORTFOLIO_COMMUNICATIONS,
            PORTFOLIO_JUDICIAL,
            MANAGE_WHATSAPP_CHATS,
        }
    ),
    UserRole.CUSTOMER_SERVICE: frozenset(
        {
            ORG_PORTFOLIOS,
            ORG_REPORTS,
            PORTFOLIO_CLIENTS,
        }
    ),
    UserRole.USER: frozenset(),
}


def get_base_permissions(role: UserRole) -> frozenset[str]:
    return ROLE_PERMISSIONS.get(role, frozenset())
