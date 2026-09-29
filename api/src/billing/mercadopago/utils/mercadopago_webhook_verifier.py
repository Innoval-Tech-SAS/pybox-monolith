from mercadopago.webhook import InvalidWebhookSignatureError, WebhookSignatureValidator

from core.config.logger import logger


def verify_mercadopago_signature(
    data_id: str, x_request_id: str | None, x_signature: str | None, webhook_secret: str
) -> bool:
    """
    Verifica la firma del webhook de Mercado Pago usando el validador oficial del SDK
    (`mercadopago.webhook.WebhookSignatureValidator`) en vez de reconstruir el HMAC a
    mano: la doc publica ya no expone la formula del manifest, solo ejemplos via SDK.

    Importante: en la Orders API el `data.id` llega en MAYUSCULAS (ej. `ORD01...`), pero
    MP firma el manifest con ese id en MINUSCULAS. El validador del SDK arma el HMAC con
    el id tal cual se le pasa, asi que hay que enviarselo en lowercase o la firma nunca
    cuadra (401 en todas las notificaciones). Para ids numericos de otros
    topicos `.lower()` es un no-op, asi que es seguro aplicarlo siempre.
    Solo se minusculiza para la firma; el `data_id` original (case-sensitive)
    se sigue usando para `get_order`.

    `webhook_secret` es el de la cuenta/pais que el controller ya resolvio por
    `application_id` antes de llamar aqui (ver mercadopago_credentials.py).
    """
    logger.info(
        "[billing][mp-verify] inicio | data_id=%s x_request_id=%s "
        "x_signature_presente=%s",
        data_id,
        x_request_id,
        bool(x_signature),
    )
    try:
        WebhookSignatureValidator.validate(
            x_signature, x_request_id, data_id.lower(), webhook_secret
        )
    except InvalidWebhookSignatureError as exc:
        logger.warning(
            "[billing][mp-verify] fin | resultado=False motivo=%s request_id=%s ts=%s",
            exc.reason.value,
            exc.request_id,
            exc.timestamp,
        )
        return False

    logger.info("[billing][mp-verify] fin | resultado=True")
    return True
