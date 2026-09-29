"""Reexporta los seeds de datos base que corre el lifespan al arrancar la app."""

from core.seed.seed_admin import seed_admin
from core.seed.seed_channels import seed_channels
from core.seed.seed_countries import seed_countries
from core.seed.seed_messaging_credentials import seed_messaging_credentials
from core.seed.seed_permissions import seed_permissions
from core.seed.seed_platform_gateway_credentials import (
    seed_platform_gateway_credentials,
)

__all__ = [
    "seed_admin",
    "seed_channels",
    "seed_countries",
    "seed_messaging_credentials",
    "seed_permissions",
    "seed_platform_gateway_credentials",
]
