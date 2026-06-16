from identity.auth.enums.auth_enums import AuthProvider
from app_platform.countries.enums.country_enums import Nationality, UserDocumentType


def normalize_email(email: str) -> str:
    return require_value(email, "El correo electrónico es obligatorio.").lower()


def normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def require_value(value: str, message: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(message)
    return normalized


def resolve_document_type(document_type: UserDocumentType | str) -> UserDocumentType:
    if isinstance(document_type, UserDocumentType):
        return document_type
    try:
        return UserDocumentType[document_type]
    except KeyError:
        pass
    try:
        return UserDocumentType(document_type)
    except ValueError as error:
        raise ValueError("El tipo de documento no es válido.") from error


def resolve_auth_provider(provider: AuthProvider | str) -> AuthProvider:
    if isinstance(provider, AuthProvider):
        return provider
    try:
        return AuthProvider[provider]
    except KeyError:
        pass
    try:
        return AuthProvider(provider)
    except ValueError as error:
        raise ValueError("El proveedor de autenticación no es válido.") from error


def mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    masked_local = local[0] + "*" * max(len(local) - 1, 3)
    domain_parts = domain.split(".")
    masked_domain = domain_parts[0][0] + "*" * max(len(domain_parts[0]) - 1, 2) if domain_parts[0] else "***"
    return f"{masked_local}@{masked_domain}.{'.'.join(domain_parts[1:])}"


def mask_phone(phone: str) -> str:
    digits = phone.replace(" ", "")
    if len(digits) <= 6:
        return "*" * len(digits)
    return digits[:4] + "*" * (len(digits) - 6) + digits[-2:]


def resolve_nationality(nationality: Nationality | str) -> Nationality:
    if isinstance(nationality, Nationality):
        return nationality
    try:
        return Nationality[nationality]
    except KeyError:
        pass
    try:
        return Nationality(nationality)
    except ValueError as error:
        raise ValueError("La nacionalidad no es válida.") from error
