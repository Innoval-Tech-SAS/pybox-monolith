"""Configuración de conexión a Postgres leída desde variables de entorno."""

from dataclasses import dataclass

from dotenv import load_dotenv

from core.tools.config_tools import get_or_throw

load_dotenv()


@dataclass
class DatabaseConfig:
    host: str = get_or_throw("DB_HOST")
    port: int = int(get_or_throw("DB_PORT"))
    username: str = get_or_throw("DB_USERNAME")
    password: str = get_or_throw("DB_PASSWORD")
    database_name: str = get_or_throw("DB_NAME")
    database_engine: str = get_or_throw("DB_ENGINE")
    database_driver: str = get_or_throw("DB_DRIVER")
    url_connection: str = (
        f"{database_engine}+{database_driver}://{username}:{password}"
        f"@{host}:{port}/{database_name}"
    )


db_config = DatabaseConfig()
