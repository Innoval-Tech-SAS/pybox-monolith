from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.error_handlers import register_error_handlers
from database.database import db
from tools.config_tools import get_or_throw

# Importar modelos para que SQLAlchemy los registre en Base.metadata antes de create_all
import campaigns.models.campaign_model  # noqa: F401
import contacts.models.contact_model  # noqa: F401
import organizations.models.organization_model  # noqa: F401
import organizations.models.organization_membership_model  # noqa: F401
import users.models.user_model  # noqa: F401
import users.models.permission_model  # noqa: F401
import users.models.role_assignment_model  # noqa: F401
import users.models.permission_assignment_model  # noqa: F401

from auth.controllers.auth_controller import router as auth_router
from contacts.controllers.contact_controller import router as contacts_router
from countries.controllers.countries_controller import router as countries_router
from users.controllers.user_controller import router as users_router

API_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.create_tables()
    yield
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

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(contacts_router, prefix=API_PREFIX)
app.include_router(countries_router, prefix=API_PREFIX)
app.include_router(users_router, prefix=API_PREFIX)


@app.get("/")
async def index() -> dict:
    return {"message": "Welcome to the API!"}
