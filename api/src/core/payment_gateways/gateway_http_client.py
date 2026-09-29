import httpx

from core.config.logger import logger


class GatewayHttpClient:
    """Base reutilizable para clientes HTTP de pasarelas de pago externas (Mercado
    Pago, Wompi, ...): un solo `httpx.AsyncClient` por subclase (singleton), reutilizado
    entre instancias y llamadas — abrir/cerrar conexion TLS por request seria el cuello
    de botella dominante en un flujo con varios intentos de pago.

    No sabe nada de facturas, cuotas, organizaciones ni credenciales: cada subclase
    decide de donde saca las suyas y que hacer con la respuesta. Setear `_LOG_TAG` en la
    subclase para que los logs de error se identifiquen por proveedor."""

    _TIMEOUT_SECONDS: float = 10
    _LOG_TAG: str = "gateway"

    def __new__(cls) -> "GatewayHttpClient":
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._http = httpx.AsyncClient(timeout=cls._TIMEOUT_SECONDS)
        return cls._instance

    def _log_error(self, response: httpx.Response, context: str) -> None:
        """Loguea el cuerpo del error antes de propagar. `raise_for_status()` descarta
        `response.text`, y sin ese detalle un 4xx del proveedor llega al cliente como un
        500 opaco imposible de diagnosticar."""
        if response.is_error:
            logger.error(
                "[%s] %s fallo | status=%s body=%s",
                self._LOG_TAG,
                context,
                response.status_code,
                response.text,
            )
