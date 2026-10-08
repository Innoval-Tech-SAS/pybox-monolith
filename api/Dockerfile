FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project

COPY src ./src
COPY alembic.ini ./
COPY alembic ./alembic

EXPOSE 5000

# --proxy-headers + --forwarded-allow-ips="*": nginx (server/nginx) es el único
# ingreso -- el puerto 5000 solo se publica en 127.0.0.1 del host (ver
# docker-compose.yaml) y dentro de la red de contenedores nadie más le habla a la
# API. Sin esto, `request.client.host` (usado por el rate limiter) es siempre la IP
# interna de nginx, no la del cliente real: el límite de intentos de login/OTP
# termina compartido entre TODOS los usuarios en vez de ser por IP. La IP de nginx
# dentro de la red de compose es dinámica, así que no hay una IP fija que listar.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips=*"]
