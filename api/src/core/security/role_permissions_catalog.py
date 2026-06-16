from identity.users.enums.user_enums import UserRole
from core.security.permissions import (
    ORG_PORTFOLIOS, ORG_PAYMENT_METHODS, ORG_REPORTS, ORG_USERS, ORG_CAMPAIGNS, ORG_TEMPLATES,
    PORTFOLIO_CLIENTS, PORTFOLIO_UPLOAD_NEW, PORTFOLIO_UPLOAD_UPDATE,
)

ROLE_PERMISSIONS: dict[UserRole, frozenset[str]] = {
    UserRole.ADMIN: frozenset({
        ORG_PORTFOLIOS, ORG_PAYMENT_METHODS, ORG_REPORTS, ORG_USERS, ORG_CAMPAIGNS, ORG_TEMPLATES,
        PORTFOLIO_CLIENTS, PORTFOLIO_UPLOAD_NEW, PORTFOLIO_UPLOAD_UPDATE,
    }),
    UserRole.CUSTOMER_SERVICE: frozenset({
        ORG_PORTFOLIOS, ORG_REPORTS,
        PORTFOLIO_CLIENTS,
    }),
    UserRole.USER_ORGANIZATION: frozenset(),
    UserRole.USER: frozenset(),
}


def get_base_permissions(role: UserRole) -> frozenset[str]:
    return ROLE_PERMISSIONS.get(role, frozenset())
