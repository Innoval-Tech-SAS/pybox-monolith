"""Defaults y sentinela de configuración no establecida para el canal IVR (Helena)."""

# Defaults de la configuración opcional del canal IVR (Helena) -- nombrados para no
# repetir el literal en cada `get_or_default`, no para desactivar la lectura de la
# variable de entorno: siguen siendo overrideables.
DEFAULT_TIMEOUT_SECONDS = "20"
DEFAULT_TIMEZONE = "America/Bogota"
DEFAULT_STALE_MINUTES = "30"

# Sentinela de "no configurado" -- a diferencia de los anteriores, un valor vacío
# aquí es un estado válido: la funcionalidad que depende de la variable se
# autodesactiva en silencio (ver helena_webhook_registrar/helena_webhook_verifier)
# en vez de impedir el arranque de la API.
UNSET = ""
