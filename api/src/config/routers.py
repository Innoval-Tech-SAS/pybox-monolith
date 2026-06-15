from fastapi import FastAPI

from auth.controllers.auth_controller import router as auth_router
from databases.controllers.database_controller import router as databases_router
from contacts.controllers.contact_controller import router as contacts_router
from debtors.controllers.debtor_controller import router as debtors_router
from countries.controllers.countries_controller import router as countries_router
from credits.controllers.my_credits_controller import router as my_credits_router
from notifications.controllers.notification_controller import router as notifications_router
from onboarding.controllers.onboarding_controller import router as onboarding_router
from organizations.controllers.organization_controller import router as organizations_router
from organizations.controllers.org_members_controller import router as org_members_router
from payment_methods.controllers.payment_method_controller import router as payment_methods_router
from portfolios.controllers.portfolio_controller import router as portfolios_router
from support.controllers.support_controller import router as support_router
from chats.controllers.chat_controller import router as chats_router
from segments.controllers.segment_controller import router as segments_router
from campaigns.controllers.campaign_controller import router as campaigns_router
from segments.controllers.segment_controller import router as segments_router
from templates.controllers.template_controller import router as templates_router
from users.controllers.global_users_controller import router as global_users_router
from users.controllers.permissions_controller import router as permissions_router
from users.controllers.user_controller import router as users_router

_API_PREFIX = "/api/v1"


def register_routers(app: FastAPI) -> None:
    app.include_router(auth_router, prefix=_API_PREFIX)
    app.include_router(contacts_router, prefix=_API_PREFIX)
    app.include_router(debtors_router, prefix=_API_PREFIX)
    app.include_router(countries_router, prefix=_API_PREFIX)
    app.include_router(my_credits_router, prefix=_API_PREFIX)
    app.include_router(notifications_router, prefix=_API_PREFIX)
    app.include_router(onboarding_router, prefix=_API_PREFIX)
    app.include_router(organizations_router, prefix=_API_PREFIX)
    app.include_router(org_members_router, prefix=_API_PREFIX)
    app.include_router(payment_methods_router, prefix=_API_PREFIX)
    app.include_router(portfolios_router, prefix=_API_PREFIX)
    app.include_router(chats_router, prefix=_API_PREFIX)
    app.include_router(support_router, prefix=_API_PREFIX)
    app.include_router(users_router, prefix=_API_PREFIX)
    app.include_router(global_users_router, prefix=_API_PREFIX)
    app.include_router(permissions_router, prefix=_API_PREFIX)
    app.include_router(databases_router, prefix=_API_PREFIX)
    app.include_router(segments_router, prefix=_API_PREFIX)
    app.include_router(campaigns_router, prefix=_API_PREFIX)
    app.include_router(segments_router, prefix=_API_PREFIX)
    app.include_router(templates_router, prefix=_API_PREFIX)
