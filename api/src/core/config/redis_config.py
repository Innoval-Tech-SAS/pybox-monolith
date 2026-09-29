"""Configuración de conexión a Redis leída desde variables de entorno."""

from dataclasses import dataclass, field
from urllib.parse import quote

from core.tools.config_tools import get_or_throw


@dataclass
class RedisConfig:
    host: str = field(default_factory=lambda: get_or_throw("REDIS_HOST"))
    port: str = field(default_factory=lambda: get_or_throw("REDIS_PORT"))
    password: str = field(default_factory=lambda: get_or_throw("REDIS_PASSWORD"))
    db: str = "0"
    DEFAULT_TTL = 10800  # 3 hours

    @property
    def url(self) -> str:
        password = quote(self.password, safe="")
        return f"redis://:{password}@{self.host}:{self.port}/{self.db}"
