from dataclasses import dataclass, field
from urllib.parse import quote

from tools.config_tools import get_or_throw


@dataclass
class RedisConfig:
    host: str = field(default_factory=lambda: get_or_throw("REDIS_HOST"))
    port: str = field(default_factory=lambda: get_or_throw("REDIS_PORT"))
    password: str = field(default_factory=lambda: get_or_throw("REDIS_PASSWORD"))
    db: str = "0"

    @property
    def url(self) -> str:
        return f"redis://:{quote(self.password, safe='')}@{self.host}:{self.port}/{self.db}"
