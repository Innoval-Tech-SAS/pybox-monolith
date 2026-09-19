# Pybox API

Backend de Pybox: FastAPI + SQLAlchemy async sobre PostgreSQL (vía PgBouncer), Redis para sesiones/cache, Alembic para migraciones. Python ≥3.14, gestionado con `uv`.

Ver también el [README del proyecto](../README.md) y las reglas de arquitectura en [CLAUDE.md](../CLAUDE.md).

## Stack

- **FastAPI** — HTTP, WebSockets (chat, chat de WhatsApp) y SSE (notificaciones en tiempo real).
- **SQLAlchemy async + asyncpg** — una sesión por request/job vía `Database.get_session()` (Unit of Work), sin `session.commit()` manual fuera de ese ciclo.
- **PgBouncer** — pool en modo `transaction` frente a Postgres; las migraciones de Alembic lo esquivan y hablan directo con `database` (ver `ALEMBIC_DB_HOST`/`ALEMBIC_DB_PORT` en `docker-compose.yaml`), porque el modo `transaction` rompe `CREATE INDEX CONCURRENTLY` y los bloques autocommit de las migraciones.
- **Redis** — sesiones y cache.
- **SeaweedFS (S3-compatible)** — almacenamiento de archivos/documentos. El gateway S3 no publica puertos en el host; solo la API lo alcanza por la red interna del compose, y los archivos se sirven al navegador vía nginx con `X-Accel-Redirect`, nunca directo.
- **Alembic** — migraciones.
- **APScheduler** — jobs programados (ej. contador diario de mora, transiciones de facturación vencida).
- **Pasarelas de pago**: Mercado Pago y Bold (`billing/`).
- **Proveedores externos**: 360NRS (SMS/Email), Helena (IVR/llamadas masivas), WhatsApp Cloud API (Meta).

## Estructura (`src/`)

```
identity/       auth, sesiones, organizaciones, usuarios, onboarding (MFA obligatorio a nivel de dependency)
app_platform/   chats, países, dashboard, documentos, notificaciones, credenciales de proveedores, soporte, schema_manager
billing/        facturación, pasarelas (Mercado Pago, Bold), tasas de cambio, dashboard de facturación
messaging/      canales, campañas, plantillas, contactos, envío masivo, WhatsApp, IVR
receivables/    portafolios, créditos, deudores, pagos, segmentos, notificaciones judiciales, reportes, estados de cuenta
core/           Repository/Model base, config, database (Unit of Work), security (policies, rate limit, tokens), storage, cache, sse
```

Cada dominio sigue la misma convención interna:

- `model/`, `repository/`, `service/`, `controller/` — clases.
- `constants/`, `utils/` — valores/funciones planas (nunca en `core/config/`).
- `schemas/` — dataclasses de entrada/salida.

Las capas, el diseño de esquema (FKs, migraciones), los anti-patrones de queries/transacciones, y el aislamiento multi-tenant por cadena de pertenencia están definidos como skills auditadas — ver [CLAUDE.md](../CLAUDE.md). Cualquier cambio bajo `src/**` debe pasar por ellas antes de darse por terminado.

## Multi-tenancy

No existe un `organization_id` plano filtrando cada tabla. El aislamiento se valida salto por salto en una cadena de pertenencia (`UserSession` → Organización → Portafolio → Crédito/Deudor → Dirección/Contacto/Documento) con los helpers de `core/security/policies/security_policies.py`. Todo endpoint autenticado que reciba un ID de recurso por path/query debe pasar por esa validación.

## Dinero

Siempre `Decimal` en Python / `Numeric(precision, scale)` en columnas. Nunca `float`/`Float`.

## Variables de entorno

Ver `.env.example` en la raíz del repo para la lista completa y comentada. Convención: las variables **requeridas** se leen con `get_or_throw` sin default; los valores de fallback opcionales son constantes de módulo en `<dominio>/constants/`, nunca `os.getenv(..., default)`.

## Desarrollo local (Podman)

El host no requiere Python instalado — todo corre en contenedores. Uso restringido a `podman compose ...` (nunca `podman` a secas).

```bash
podman compose up -d --build api
podman compose exec api alembic upgrade head
podman compose logs -f api
```

Tras reconstruir la imagen de `api`, reiniciar `template-nginx` (el DNS interno queda obsoleto y produce 502).

### Migraciones

```bash
podman compose exec api alembic revision --autogenerate -m "descripción"
podman compose exec api alembic upgrade head
```

### Tests

```bash
podman compose exec api pytest
podman compose exec api pytest --cov
```

Los tests viven en `tests/`, reflejando la ruta de `src/` — nunca junto al código fuente. `pytest-asyncio` en modo `auto`.

## Endpoints en tiempo real

Expuestos vía WebSocket/SSE y enrutados aparte en `server/nginx` (timeouts largos, sin buffering):

- `GET /api/v1/chats/ws` — chat interno 1 a 1.
- `GET /api/v1/whatsapp/chats/ws` — chat en vivo de WhatsApp.
- `GET /api/v1/notifications/stream` — notificaciones (SSE).
