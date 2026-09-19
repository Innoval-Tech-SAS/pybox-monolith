ACCESS_TOKEN_COOKIE = "access_token"
REFRESH_TOKEN_COOKIE = "refresh_token"

# Debe coincidir con API_PREFIX ("/api/v1") + el prefijo del router de auth ("/auth")
# en core/config/routers.py. No se importa de ahí para evitar un ciclo de imports
# (routers.py importa los controllers, que importan core.security.utils.cookie_utils).
REFRESH_TOKEN_PATH = "/api/v1/auth"
