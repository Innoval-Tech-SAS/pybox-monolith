from fastapi import FastAPI

from auth.controllers.auth_controller import router as auth_router
from contacts.controllers.contact_controller import router as contacts_router
from countries.controllers.countries_controller import router as countries_router
from credits.controllers.my_credits_controller import router as my_credits_router
from notifications.controllers.notification_controller import router as notifications_router
from onboarding.controllers.onboarding_controller import router as onboarding_router
from organizations.controllers.organization_controller import router as organizations_router
from organizations.controllers.org_members_controller import router as org_members_router
from portfolios.controllers.portfolio_controller import router as portfolios_router
from support.controllers.support_controller import router as support_router
from users.controllers.global_users_controller import router as global_users_router
from users.controllers.permissions_controller import router as permissions_router
from users.controllers.user_controller import router as users_router

_API_PREFIX = "/api/v1"


def register_routers(app: FastAPI) -> None:
    app.include_router(auth_router, prefix=_API_PREFIX)
    app.include_router(contacts_router, prefix=_API_PREFIX)
    app.include_router(countries_router, prefix=_API_PREFIX)
    app.include_router(my_credits_router, prefix=_API_PREFIX)
    app.include_router(notifications_router, prefix=_API_PREFIX)
    app.include_router(onboarding_router, prefix=_API_PREFIX)
    app.include_router(organizations_router, prefix=_API_PREFIX)
    app.include_router(org_members_router, prefix=_API_PREFIX)
    app.include_router(portfolios_router, prefix=_API_PREFIX)
    app.include_router(support_router, prefix=_API_PREFIX)
    app.include_router(users_router, prefix=_API_PREFIX)
    app.include_router(global_users_router, prefix=_API_PREFIX)
    app.include_router(permissions_router, prefix=_API_PREFIX)
