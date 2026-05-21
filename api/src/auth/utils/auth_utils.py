from auth.enums.auth_enums import AuthProvider
from countries.enums.country_enums import Nationality, UserDocumentType


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
