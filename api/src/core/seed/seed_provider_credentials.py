import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.provider_credentials.enums.provider_credential_enums import CredentialProvider
from app_platform.provider_credentials.models.provider_credential_model import ProviderCredentialModel
from core.config.logger import logger
from core.security.services.encrypt_service import encrypt_service


def _env(key: str) -> str:
    return (os.getenv(key) or "").strip()


# Credenciales GLOBALES (country_code=None) sembradas desde las env vars actuales.
# Cada spec: (provider, {clave_secreta: env_var}, {clave_publica: env_var}).
# MercadoPago/Bold se siembran en la Fase 4 (migración de pasarelas).
_SPECS: list[tuple[CredentialProvider, dict[str, str], dict[str, str]]] = [
    (
        CredentialProvider.NRS360_SMS,
        {"token": "NRS360_SMS_TOKEN"},
        {"sender": "NRS360_SMS_SENDER"},
    ),
    (
        CredentialProvider.NRS360_EMAIL,
        {"token": "NRS360_EMAIL_TOKEN"},
        {"sender": "NRS360_EMAIL_SENDER", "sender_name": "NRS360_EMAIL_SENDER_NAME"},
    ),
    (
        CredentialProvider.WHATSAPP_CLOUD,
        {"access_token": "WHATSAPP_CLOUD_ACCESS_TOKEN", "app_secret": "WHATSAPP_CLOUD_APP_SECRET"},
        {"waba_id": "WHATSAPP_CLOUD_WABA_ID"},
    ),
]


async def seed_provider_credentials(session: AsyncSession) -> None:
    existing = {
        (row[0], row[1])
        for row in (
            await session.execute(
                select(ProviderCredentialModel.country_code, ProviderCredentialModel.provider)
            )
        ).all()
    }

    seeded = 0
    for provider, secret_env, public_env in _SPECS:
        if (None, provider) in existing:
            continue
        secret_values = {key: _env(var) for key, var in secret_env.items()}
        # Env parcialmente configurado no debe crear una credencial inválida; se omite
        # y el envío por ese proveedor caerá al fallback de env (Fase 3b).
        if any(not value for value in secret_values.values()):
            logger.warning(
                "[seed] provider_credential_skipped | provider=%s (secreto faltante en env)",
                provider.value,
            )
            continue
        session.add(
            ProviderCredentialModel(
                country_code=None,
                provider=provider,
                secrets={key: encrypt_service.encrypt_to_str(value) for key, value in secret_values.items()},
                public_config={key: _env(var) for key, var in public_env.items()},
            )
        )
        seeded += 1

    # MercadoPago MX: por país (no global), con lookup_key = application_id para que el
    # webhook resuelva la cuenta antes de verificar la firma. secretos = access_token +
    # webhook_secret; no secretos (van al frontend / se buscan por igualdad) = public_key
    # + application_id.
    if ("MX", CredentialProvider.MERCADOPAGO) not in existing:
        mp_access = _env("MP_ACCESS_TOKEN_MX")
        mp_secret = _env("MP_WEBHOOK_SECRET_MX")
        mp_public = _env("MP_PUBLIC_KEY_MX")
        mp_app_id = _env("MP_APPLICATION_ID_MX")
        if mp_access and mp_secret and mp_app_id:
            session.add(
                ProviderCredentialModel(
                    country_code="MX",
                    provider=CredentialProvider.MERCADOPAGO,
                    secrets={
                        "access_token": encrypt_service.encrypt_to_str(mp_access),
                        "webhook_secret": encrypt_service.encrypt_to_str(mp_secret),
                    },
                    public_config={"public_key": mp_public, "application_id": mp_app_id},
                    lookup_key=mp_app_id,
                )
            )
            seeded += 1
        else:
            logger.warning("[seed] provider_credential_skipped | provider=mercadopago MX (env incompleto)")

    if seeded:
        await session.commit()
    logger.info("[seed] provider_credentials_seeded | nuevos=%d", seeded)
