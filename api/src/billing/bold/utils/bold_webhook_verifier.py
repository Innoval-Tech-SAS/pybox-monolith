import base64
import hashlib
import hmac

from core.tools.config_tools import get_or_throw


def verify_bold_signature(raw_body: bytes, signature: str | None) -> bool:
    """
    Verifica la firma del webhook de Bold.

    Algoritmo: HMAC-SHA256(Base64(rawBody), secretKey), comparado contra el
    header x-bold-signature. En modo sandbox, Bold firma con una llave secreta
    vacia, por lo que BOLD_SECRET_KEY puede estar vacia sin error.
    Docs: https://developers.bold.co/webhook
    """
    if not signature:
        return False
    secret_key = get_or_throw("BOLD_SECRET_KEY")
    encoded = base64.b64encode(raw_body)
    digest = hmac.new(secret_key.encode("utf-8"), encoded, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, signature)
