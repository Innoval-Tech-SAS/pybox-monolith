"""Límites y formato de enmascarado para la verificación de identidad del deudor."""

# Tope de intentos de verificación por documento, sin importar quién llame. Es la
# defensa del lado API contra fuerza bruta del dato de confirmación (n8n aplica su
# propio límite por conversación, pero un fallo de ese lado no debe dejar el dato
# adivinable).
IDENTITY_VERIFY_MAX_ATTEMPTS = 5
IDENTITY_VERIFY_WINDOW_SECONDS = 3600
IDENTITY_VERIFY_KEY_PREFIX = "identity_verify"

# Un número de teléfono se compara por sus últimos dígitos: en base de datos puede
# venir con o sin indicativo de país.
PHONE_COMPARE_DIGITS = 10
PHONE_MIN_DIGITS = 7
PHONE_VISIBLE_DIGITS = 4

# Caracteres del correo que se dejan visibles al inicio de la parte local.
EMAIL_VISIBLE_CHARS = 2
MASK_CHAR = "*"
