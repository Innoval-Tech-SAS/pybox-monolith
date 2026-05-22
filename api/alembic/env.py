import asyncio
import os
import sys

from dotenv import load_dotenv
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# Añadir src/ al path para que los imports de los modelos funcionen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

load_dotenv()

# Importar todos los modelos para que Alembic los detecte en Base.metadata
from database.database import Base  # noqa: E402
import campaigns.models.campaign_model  # noqa: E402, F401
import contacts.models.contact_model  # noqa: E402, F401
import notifications.models.verification_code_model  # noqa: E402, F401
import organizations.models.organization_model  # noqa: E402, F401
import organizations.models.organization_membership_model  # noqa: E402, F401
import users.models.user_model  # noqa: E402, F401
import users.models.permission_model  # noqa: E402, F401
import users.models.role_assignment_model  # noqa: E402, F401
import users.models.permission_assignment_model  # noqa: E402, F401
import countries.models.country_model  # noqa: E402, F401
import portfolios.models.portfolio_model  # noqa: E402, F401
import portfolios.models.portfolio_user_access_model  # noqa: E402, F401
import portfolios.models.portfolio_daily_counter_config_model  # noqa: E402, F401
import debtors.models.debtor_model  # noqa: E402, F401
import debtors.models.address_model  # noqa: E402, F401
import debtors.models.segment_model  # noqa: E402, F401
import credits.models.credit_model  # noqa: E402, F401
import credits.models.credit_adjustment_model  # noqa: E402, F401
import credits.models.uvr_quote_model  # noqa: E402, F401
import payments.models.payment_model  # noqa: E402, F401
import payment_methods.models.payment_method_model  # noqa: E402, F401
import contact_methods.models.contact_method_model  # noqa: E402, F401
import reports.models.report_model  # noqa: E402, F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Construir la URL desde las variables de entorno del proyecto
def _get_url() -> str:
    engine = os.environ["DB_ENGINE"]
    driver = os.environ["DB_DRIVER"]
    user = os.environ["DB_USERNAME"]
    password = os.environ["DB_PASSWORD"]
    host = os.environ["DB_HOST"]
    port = os.environ["DB_PORT"]
    name = os.environ["DB_NAME"]
    return f"{engine}+{driver}://{user}:{password}@{host}:{port}/{name}"


def run_migrations_offline() -> None:
    context.configure(
        url=_get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(_get_url())
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
