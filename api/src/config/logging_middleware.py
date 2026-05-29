import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from config.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        logger.info("→ %s %s", request.method, request.url.path)
        try:
            response = await call_next(request)
        except Exception as exc:
            elapsed = int((time.perf_counter() - start) * 1000)
            logger.exception("← 500 %s %s (%dms)", request.method, request.url.path, elapsed)
            raise exc
        elapsed = int((time.perf_counter() - start) * 1000)
        level = logger.error if response.status_code >= 500 else logger.warning if response.status_code >= 400 else logger.info
        level("← %d %s %s (%dms)", response.status_code, request.method, request.url.path, elapsed)
        return response
