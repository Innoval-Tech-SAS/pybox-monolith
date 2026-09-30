"""Excepciones del ciclo de vida de un código de verificación (OTP)."""


class CodeNotFoundException(Exception):
    pass


class CodeExpiredException(Exception):
    pass


class CodeAlreadyUsedException(Exception):
    pass
