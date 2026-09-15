from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.countries.enums.country_enums import Nationality
from app_platform.provider_credentials.enums.provider_credential_enums import CredentialProvider
from app_platform.provider_credentials.services.provider_credential_service import (
    DecryptedCredential,
    ProviderCredentialService,
)
from core.tools.config_tools import get_or_default

# Sentinel de "no configurada por env" -- `_load_credentials` trata cualquier campo
# vacío como ausente (ver el `if not (...)` de abajo), así que el default real es
# "no hay fallback", no un valor de negocio.
_ENV_FALLBACK_UNSET = ""


@dataclass(frozen=True)
class MercadoPagoCredentials:
    """
    Cada pais que opera con Mercado Pago tiene su propia cuenta/aplicacion (access
    token, public key, application_id y webhook secret propios). El application_id
    es lo que permite al webhook, que solo recibe `data.id` y el body de MP, resolver
    a que pais/cuenta pertenece una notificacion antes de verificar su firma.

    Fuente de verdad: la tabla `credenciales_proveedor` (cifrada). Las funciones
    `resolve_credentials_*` leen de DB y descifran; si no hay fila, caen a las env vars
    `MP_*_<CC>` (fallback para no romper cobros durante la migración).
    """

    country: str | None
    access_token: str
    public_key: str
    application_id: str
    webhook_secret: str


# ── Fallback por variables de entorno (suave: no revienta el arranque si faltan) ──

def _load_credentials(country: str, env_suffix: str) -> MercadoPagoCredentials | None:
    access_token = get_or_default(f"MP_ACCESS_TOKEN_{env_suffix}", _ENV_FALLBACK_UNSET)
    application_id = get_or_default(f"MP_APPLICATION_ID_{env_suffix}", _ENV_FALLBACK_UNSET)
    webhook_secret = get_or_default(f"MP_WEBHOOK_SECRET_{env_suffix}", _ENV_FALLBACK_UNSET)
    if not (access_token and application_id and webhook_secret):
        return None
    return MercadoPagoCredentials(
        country=country,
        access_token=access_token,
        public_key=get_or_default(f"MP_PUBLIC_KEY_{env_suffix}", _ENV_FALLBACK_UNSET),
        application_id=application_id,
        webhook_secret=webhook_secret,
    )


_CREDENTIALS_BY_COUNTRY: dict[str, MercadoPagoCredentials] = {
    country: credentials
    for country, credentials in [(Nationality.MX.value, _load_credentials(Nationality.MX.value, "MX"))]
    if credentials is not None
}

_CREDENTIALS_BY_APPLICATION_ID: dict[str, MercadoPagoCredentials] = {
    credentials.application_id: credentials for credentials in _CREDENTIALS_BY_COUNTRY.values()
}


def get_credentials_for_country(country: str | None) -> MercadoPagoCredentials | None:
    if country is None:
        return None
    return _CREDENTIALS_BY_COUNTRY.get(country)


def get_credentials_for_application_id(application_id: str) -> MercadoPagoCredentials | None:
    credentials = _CREDENTIALS_BY_APPLICATION_ID.get(application_id)
    if credentials is not None:
        return credentials

    # En sandbox el `application_id` del body varia segun el origen: el simulador y
    # produccion mandan el de la app real (p.ej. 7273...), pero un pago real de prueba
    # llega con el del usuario de prueba/vendedor (p.ej. 8811...). Como la firma igual
    # se valida despues con el `webhook_secret`, si solo hay una cuenta configurada la
    # usamos como fallback en vez de rechazar por id (falsear el id no gana nada sin el
    # secret). Con varias cuentas si exigimos match exacto para no cruzar paises.
    if len(_CREDENTIALS_BY_COUNTRY) == 1:
        return next(iter(_CREDENTIALS_BY_COUNTRY.values()))

    return None


# ── Resolución desde DB (fuente de verdad), con fallback a env ──

def _from_decrypted(cred: DecryptedCredential) -> MercadoPagoCredentials | None:
    access_token = cred.get("access_token")
    webhook_secret = cred.get("webhook_secret")
    application_id = cred.get("application_id")
    if not (access_token and webhook_secret and application_id):
        return None
    return MercadoPagoCredentials(
        country=cred.country_code,
        access_token=access_token,
        public_key=cred.get("public_key") or "",
        application_id=application_id,
        webhook_secret=webhook_secret,
    )


async def resolve_credentials_for_country(
    session: AsyncSession, country: str | None
) -> MercadoPagoCredentials | None:
    if country is not None:
        cred = await ProviderCredentialService(session).get_decrypted(
            country, CredentialProvider.MERCADOPAGO
        )
        if cred is not None:
            mp = _from_decrypted(cred)
            if mp is not None:
                return mp
    return get_credentials_for_country(country)


async def resolve_credentials_for_application_id(
    session: AsyncSession, application_id: str
) -> MercadoPagoCredentials | None:
    cred = await ProviderCredentialService(session).resolve_by_lookup_key(
        CredentialProvider.MERCADOPAGO, application_id
    )
    if cred is not None:
        mp = _from_decrypted(cred)
        if mp is not None:
            return mp
    # Fallback env: incluye la lógica de "cuenta única" para el application_id de sandbox.
    return get_credentials_for_application_id(application_id)
