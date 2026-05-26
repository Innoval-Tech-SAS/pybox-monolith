import asyncio
import contextlib
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config.error_handlers import register_error_handlers
from config.paths import UPLOADS_ROOT
from database.database import db
from database.session_expiry_listener import start_session_expiry_listener
from security.seed_permissions import seed_permissions
from tools.config_tools import get_or_throw

import campaigns.models.campaign_model  # noqa: F401
import contacts.models.contact_model  # noqa: F401
import messaging.models.verification_code_model  # noqa: F401
import organizations.models.organization_model  # noqa: F401
import organizations.models.organization_membership_model  # noqa: F401
import users.models.user_model  # noqa: F401
import users.models.permission_model  # noqa: F401
import users.models.role_assignment_model  # noqa: F401
import users.models.permission_assignment_model  # noqa: F401
import users.models.user_preferences_model  # noqa: F401
import portfolios.models.portfolio_model  # noqa: F401
import portfolios.models.portfolio_user_access_model  # noqa: F401
import portfolios.models.portfolio_daily_counter_config_model  # noqa: F401
import debtors.models.debtor_model  # noqa: F401
import debtors.models.address_model  # noqa: F401
import debtors.models.segment_model  # noqa: F401
import credits.models.credit_model  # noqa: F401
import credits.models.credit_adjustment_model  # noqa: F401
import credits.models.uvr_quote_model  # noqa: F401
import payments.models.payment_model  # noqa: F401
import payment_methods.models.payment_method_model  # noqa: F401
import contact_methods.models.contact_method_model  # noqa: F401
import reports.models.report_model  # noqa: F401
import support.models.support_ticket_model  # noqa: F401
import notifications.models.notification_model  # noqa: F401

from auth.controllers.auth_controller import router as auth_router
from notifications.controllers.notification_controller import router as notifications_router
from support.controllers.support_controller import router as support_router
from contacts.controllers.contact_controller import router as contacts_router
from countries.controllers.countries_controller import router as countries_router
from credits.controllers.my_credits_controller import router as my_credits_router
from onboarding.controllers.onboarding_controller import router as onboarding_router
from organizations.controllers.organization_controller import router as organizations_router
from organizations.controllers.org_members_controller import router as org_members_router
from portfolios.controllers.portfolio_controller import router as portfolios_router
from users.controllers.user_controller import router as users_router
from users.controllers.global_users_controller import router as global_users_router

API_PREFIX = "/api/v1"

os.makedirs(UPLOADS_ROOT, exist_ok=True)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await db.create_tables()
    async with db.get_session() as session:
        await seed_permissions(session)
    expiry_task = await start_session_expiry_listener()
    yield
    expiry_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await expiry_task
    await db.engine.dispose()


app = FastAPI(
    title="API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_or_throw("CORS_ORIGINS").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Origin", "X-Requested-With", "Content-Type", "Accept", "Authorization"],
)

register_error_handlers(app)

app.mount("/files", StaticFiles(directory=UPLOADS_ROOT), name="uploads")

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(contacts_router, prefix=API_PREFIX)
app.include_router(countries_router, prefix=API_PREFIX)
app.include_router(my_credits_router, prefix=API_PREFIX)
app.include_router(onboarding_router, prefix=API_PREFIX)
app.include_router(organizations_router, prefix=API_PREFIX)
app.include_router(portfolios_router, prefix=API_PREFIX)
app.include_router(users_router, prefix=API_PREFIX)
app.include_router(global_users_router, prefix=API_PREFIX)
app.include_router(org_members_router, prefix=API_PREFIX)
app.include_router(notifications_router, prefix=API_PREFIX)
app.include_router(support_router, prefix=API_PREFIX)


@app.get("/")
async def index() -> dict:
    return {"message": "Welcome to the API!"}
