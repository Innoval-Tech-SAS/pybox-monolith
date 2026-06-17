from fastapi import FastAPI

from identity.auth.controllers.auth_controller import router as auth_router
from app_platform.schema_manager.controllers.database_controller import router as schema_manager_router
from messaging.contacts.controllers.contact_controller import router as contacts_router
from receivables.debtors.controllers.debtor_controller import router as debtors_router
from app_platform.countries.controllers.countries_controller import router as countries_router
from receivables.credits.controllers.my_credits_controller import router as my_credits_router
from app_platform.notifications.controllers.notification_controller import router as notifications_router
from identity.onboarding.controllers.onboarding_controller import router as onboarding_router
from identity.organizations.controllers.organization_controller import router as organizations_router
from identity.organizations.controllers.org_members_controller import router as org_members_router
from finance.payment_methods.controllers.payment_method_controller import router as payment_methods_router
from receivables.portfolios.controllers.portfolio_controller import router as portfolios_router
from app_platform.support.controllers.support_controller import router as support_router
from app_platform.chats.controllers.chat_controller import router as chats_router
from receivables.segments.controllers.segment_controller import router as segments_router
from receivables.reports.controllers.report_controller import router as reports_router
from messaging.campaigns.controllers.campaign_controller import router as campaigns_router
from messaging.channels.controllers.channel_controller import router as channels_router
from messaging.templates.controllers.template_controller import router as templates_router
from messaging.results.controllers.results_controller import router as results_router
from identity.users.controllers.global_users_controller import router as global_users_router
from identity.users.controllers.permissions_controller import router as permissions_router
from identity.users.controllers.user_controller import router as users_router

API_PREFIX = "/api/v1"


def register_routers(app: FastAPI) -> None:
    app.include_router(auth_router, prefix=API_PREFIX)
    app.include_router(contacts_router, prefix=API_PREFIX)
    app.include_router(debtors_router, prefix=API_PREFIX)
    app.include_router(countries_router, prefix=API_PREFIX)
    app.include_router(my_credits_router, prefix=API_PREFIX)
    app.include_router(notifications_router, prefix=API_PREFIX)
    app.include_router(onboarding_router, prefix=API_PREFIX)
    app.include_router(organizations_router, prefix=API_PREFIX)
    app.include_router(org_members_router, prefix=API_PREFIX)
    app.include_router(payment_methods_router, prefix=API_PREFIX)
    app.include_router(portfolios_router, prefix=API_PREFIX)
    app.include_router(chats_router, prefix=API_PREFIX)
    app.include_router(support_router, prefix=API_PREFIX)
    app.include_router(users_router, prefix=API_PREFIX)
    app.include_router(global_users_router, prefix=API_PREFIX)
    app.include_router(permissions_router, prefix=API_PREFIX)
    app.include_router(schema_manager_router, prefix=API_PREFIX)
    app.include_router(segments_router, prefix=API_PREFIX)
    app.include_router(reports_router, prefix=API_PREFIX)
    app.include_router(campaigns_router, prefix=API_PREFIX)
    app.include_router(channels_router, prefix=API_PREFIX)
    app.include_router(templates_router, prefix=API_PREFIX)
    app.include_router(results_router, prefix=API_PREFIX)
