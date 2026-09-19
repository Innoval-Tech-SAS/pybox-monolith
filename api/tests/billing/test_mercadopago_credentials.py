"""get_credentials_for_application_id es sincrona y pura sobre los diccionarios de modulo
`_CREDENTIALS_BY_COUNTRY`/`_CREDENTIALS_BY_APPLICATION_ID`, construidos una sola vez al
importar desde env vars (ver `_load_credentials`). Para no depender de que variables de
entorno reales esten seteadas, se parchan esos diccionarios directamente via
`monkeypatch.setattr` sobre el modulo -- unitario puro, sin red ni DB.

`resolve_credentials_for_country`/`resolve_credentials_for_application_id` en cambio se
prueban con `db_session` REAL (fuente de verdad: tabla `credenciales_proveedor`,
cifrada), confirmando que la DB tiene prioridad sobre el fallback de env y que una
credencial inactiva/incompleta cae al fallback en vez de romper el cobro."""

from app_platform.provider_credentials.enums.provider_credential_enums import CredentialProvider
from app_platform.provider_credentials.models.provider_credential_model import ProviderCredentialModel
from core.security.services.encrypt_service import encrypt_service
from billing.mercadopago.utils import mercadopago_credentials as mp_credentials
from billing.mercadopago.utils.mercadopago_credentials import (
    MercadoPagoCredentials,
    get_credentials_for_application_id,
    resolve_credentials_for_application_id,
    resolve_credentials_for_country,
)


async def _add_credential(
    db_session,
    *,
    country_code: str | None,
    provider: CredentialProvider = CredentialProvider.MERCADOPAGO,
    secrets: dict[str, str] | None = None,
    public_config: dict | None = None,
    lookup_key: str | None = None,
    is_active: bool = True,
) -> ProviderCredentialModel:
    secrets = secrets if secrets is not None else {"access_token": "tok", "webhook_secret": "whsec"}
    row = ProviderCredentialModel(
        country_code=country_code,
        provider=provider,
        secrets={key: encrypt_service.encrypt_to_str(value) for key, value in secrets.items()},
        public_config=public_config or {"public_key": "pub", "application_id": "APP-ID"},
        lookup_key=lookup_key,
        is_active=is_active,
    )
    db_session.add(row)
    await db_session.flush()
    return row


def _cred(application_id: str, country: str) -> MercadoPagoCredentials:
    return MercadoPagoCredentials(
        country=country, access_token="tok", public_key="pub", application_id=application_id,
        webhook_secret="secret",
    )


class TestGetCredentialsForApplicationId:
    def test_exact_application_id_match(self, monkeypatch):
        mx = _cred("APP-MX", "MX")
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_COUNTRY", {"MX": mx})
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_APPLICATION_ID", {"APP-MX": mx})

        assert get_credentials_for_application_id("APP-MX") is mx

    def test_unknown_id_falls_back_to_single_configured_account(self, monkeypatch):
        mx = _cred("APP-MX", "MX")
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_COUNTRY", {"MX": mx})
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_APPLICATION_ID", {"APP-MX": mx})

        # ej. application_id del usuario de prueba en sandbox, distinto del de la app real.
        assert get_credentials_for_application_id("APP-SANDBOX-DIFFERENT") is mx

    def test_unknown_id_with_zero_accounts_returns_none(self, monkeypatch):
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_COUNTRY", {})
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_APPLICATION_ID", {})

        assert get_credentials_for_application_id("ANYTHING") is None

    def test_unknown_id_with_multiple_accounts_returns_none(self, monkeypatch):
        mx = _cred("APP-MX", "MX")
        co = _cred("APP-CO", "CO")
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_COUNTRY", {"MX": mx, "CO": co})
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_APPLICATION_ID", {"APP-MX": mx, "APP-CO": co})

        # No se puede adivinar a que pais pertenece: con >1 cuenta se exige match exacto.
        assert get_credentials_for_application_id("APP-UNKNOWN") is None


class TestResolveCredentialsForCountry:
    # Se usa "AR" (no "MX") para las filas insertadas por estos tests: el seed real
    # (seed_provider_credentials, sembrado una vez por sesion de pytest) puede haber
    # creado ya una fila (MX, MERCADOPAGO) desde las env vars reales del proyecto, y
    # esa combinacion tiene un UniqueConstraint -- insertar otra chocaria. "AR" nunca
    # se siembra para Mercado Pago.

    async def test_country_none_returns_none_without_querying_db(self, db_session):
        assert await resolve_credentials_for_country(db_session, None) is None

    async def test_db_credential_takes_priority_over_env_fallback(self, db_session, monkeypatch):
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_COUNTRY", {"AR": mp_credentials.MercadoPagoCredentials(
            country="AR", access_token="ENV-TOKEN", public_key="env-pub",
            application_id="ENV-APP", webhook_secret="env-whsec",
        )})
        await _add_credential(
            db_session, country_code="AR",
            secrets={"access_token": "DB-TOKEN", "webhook_secret": "db-whsec"},
            public_config={"public_key": "db-pub", "application_id": "DB-APP"},
        )

        result = await resolve_credentials_for_country(db_session, "AR")

        assert result.access_token == "DB-TOKEN"
        assert result.webhook_secret == "db-whsec"
        assert result.application_id == "DB-APP"
        assert result.country == "AR"

    async def test_inactive_db_credential_falls_back_to_env(self, db_session, monkeypatch):
        fallback = MercadoPagoCredentials(
            country="AR", access_token="ENV-TOKEN", public_key="env-pub",
            application_id="ENV-APP", webhook_secret="env-whsec",
        )
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_COUNTRY", {"AR": fallback})
        await _add_credential(db_session, country_code="AR", is_active=False)

        result = await resolve_credentials_for_country(db_session, "AR")

        assert result is fallback

    async def test_incomplete_db_credential_falls_back_to_env(self, db_session, monkeypatch):
        """Fila activa pero sin webhook_secret: `_from_decrypted` la descarta (no es una
        credencial usable) en vez de dejar pasar un MercadoPagoCredentials a medias."""
        fallback = MercadoPagoCredentials(
            country="AR", access_token="ENV-TOKEN", public_key="env-pub",
            application_id="ENV-APP", webhook_secret="env-whsec",
        )
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_COUNTRY", {"AR": fallback})
        await _add_credential(db_session, country_code="AR", secrets={"access_token": "DB-TOKEN"})

        result = await resolve_credentials_for_country(db_session, "AR")

        assert result is fallback

    async def test_no_db_and_no_env_returns_none(self, db_session, monkeypatch):
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_COUNTRY", {})

        assert await resolve_credentials_for_country(db_session, "PE") is None

    async def test_global_db_credential_used_when_no_country_specific_row(self, db_session, monkeypatch):
        """`ProviderCredentialRepository.resolve` cae a la fila global (country_code
        NULL) si no hay una especifica del pais -- prioridad de DB, antes de tocar env."""
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_COUNTRY", {})
        await _add_credential(
            db_session, country_code=None,
            secrets={"access_token": "GLOBAL-TOKEN", "webhook_secret": "global-whsec"},
            public_config={"public_key": "global-pub", "application_id": "GLOBAL-APP"},
        )

        result = await resolve_credentials_for_country(db_session, "PE")

        assert result.access_token == "GLOBAL-TOKEN"
        assert result.country is None  # el country del registro DB, no el pais consultado


class TestResolveCredentialsForApplicationId:
    # Mismo motivo que arriba: se usa "AR" para las filas propias, no "MX".

    async def test_db_lookup_key_match_takes_priority(self, db_session, monkeypatch):
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_APPLICATION_ID", {})
        await _add_credential(
            db_session, country_code="AR", lookup_key="APP-AR-DB",
            secrets={"access_token": "DB-TOKEN", "webhook_secret": "db-whsec"},
            public_config={"public_key": "db-pub", "application_id": "APP-AR-DB"},
        )

        result = await resolve_credentials_for_application_id(db_session, "APP-AR-DB")

        assert result.access_token == "DB-TOKEN"
        assert result.application_id == "APP-AR-DB"

    async def test_unmatched_application_id_falls_back_to_env_single_account(self, db_session, monkeypatch):
        fallback = MercadoPagoCredentials(
            country="AR", access_token="ENV-TOKEN", public_key="env-pub",
            application_id="APP-AR-ENV", webhook_secret="env-whsec",
        )
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_COUNTRY", {"AR": fallback})
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_APPLICATION_ID", {"APP-AR-ENV": fallback})

        result = await resolve_credentials_for_application_id(db_session, "APP-SANDBOX-DIFFERENT")

        assert result is fallback

    async def test_inactive_db_row_falls_back_to_env(self, db_session, monkeypatch):
        fallback = MercadoPagoCredentials(
            country="AR", access_token="ENV-TOKEN", public_key="env-pub",
            application_id="APP-AR-DB", webhook_secret="env-whsec",
        )
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_APPLICATION_ID", {"APP-AR-DB": fallback})
        await _add_credential(db_session, country_code="AR", lookup_key="APP-AR-DB", is_active=False)

        result = await resolve_credentials_for_application_id(db_session, "APP-AR-DB")

        assert result is fallback

    async def test_no_match_anywhere_returns_none(self, db_session, monkeypatch):
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_COUNTRY", {})
        monkeypatch.setattr(mp_credentials, "_CREDENTIALS_BY_APPLICATION_ID", {})

        assert await resolve_credentials_for_application_id(db_session, "ANYTHING") is None
