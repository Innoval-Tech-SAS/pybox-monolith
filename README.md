# Pybox

Plataforma SaaS multi-tenant de gestión de cartera y cobranza. Permite a organizaciones administrar portafolios, créditos y deudores, automatizar la comunicación de cobranza (email, SMS, WhatsApp, IVR), procesar pagos y facturación, y dar seguimiento judicial a la cartera vencida — todo aislado por organización dentro de una misma instancia.

Es el monolito de destino de la migración del proyecto de microservicios `pybox`.

## Arquitectura

Monolito modular desplegado en contenedores Podman, con cuatro componentes independientes:

| Componente | Descripción | README |
|---|---|---|
| **`api/`** | Backend FastAPI (Python ≥3.14, `uv`) con SQLAlchemy async sobre PostgreSQL (vía PgBouncer), Redis para sesiones/cache y migraciones con Alembic. | [api/README.md](api/README.md) |
| **`client/`** | Frontend React 19 + TypeScript + Vite + Tailwind v4, basado en el template TailAdmin, gestionado con `pnpm`. | [client/README.md](client/README.md) |
| **`landing/`** | Sitio de marketing en HTML/CSS/JS vanilla, sin build. | [landing/README.md](landing/README.md) |
| **`server/`** | Reverse proxy nginx (certificados locales `pybox.local`) y overrides de compose para desarrollo local. | — |

Almacenamiento de archivos vía SeaweedFS (S3-compatible): el gateway S3 no publica ningún puerto en el host, solo lo alcanza la API por la red interna del compose, y se sirve al navegador vía nginx con `X-Accel-Redirect` — nunca expuesto directo. Pasarelas de pago: Mercado Pago y Bold.

## Dominios del backend (`api/src/`)

| Dominio | Responsabilidad |
|---|---|
| `identity` | Autenticación, sesiones, organizaciones, usuarios, onboarding (MFA obligatorio) |
| `app_platform` | Chats, países, dashboard, documentos, notificaciones, credenciales de proveedores, soporte, gestión de esquemas de base de datos |
| `billing` | Facturación, pasarelas de pago (Mercado Pago, Bold), tasas de cambio, dashboard de facturación |
| `messaging` | Canales, campañas, plantillas, contactos, envío masivo, WhatsApp, IVR (diseñador de flujos, monitor, reportes) |
| `receivables` | Portafolios, créditos, deudores, pagos, segmentos, notificaciones judiciales, reportes, estados de cuenta |
| `core` | Base compartida: modelos/repositorios base, configuración, unit of work, seguridad, storage, cache, SSE |

## Multi-tenancy

El aislamiento entre organizaciones no depende de un `organization_id` plano por tabla: se valida como una cadena de pertenencia (sesión de usuario → organización → portafolio → crédito/deudor → dirección/contacto/documento), verificada en cada salto por las políticas de autorización de `core/security`.

## Convenciones del proyecto

- **Dinero**: siempre `Decimal` en Python / `Numeric(precision, scale)` en columnas — nunca `float`.
- **Estructura de módulo backend**: `model/repository/service/controller` como clases; `constants/utils` como valores/funciones planas; `schemas` como dataclasses de entrada/salida.
- **Tests**: siempre en `tests/`, reflejando la ruta de `src/` — nunca junto al código fuente. Backend con `pytest` (`pytest-asyncio`), frontend con `vitest`.
- **Transacciones**: una sesión por request/job; sin commits manuales fuera de ese ciclo de vida.

Las reglas completas de arquitectura, diseño de esquema, anti-patrones y aislamiento multi-tenant viven como skills auditadas en `.claude/` — ver [CLAUDE.md](CLAUDE.md).

## Servicios y puertos (desarrollo local)

Todo el entorno corre en contenedores Podman — el host no requiere Python ni Node/npm instalados.

| Servicio | Host local | Dominio (vía `server/`) |
|---|---|---|
| `landing` | `127.0.0.1:8081` | `https://pybox.local` |
| `client` | `127.0.0.1:8083` | `https://app.pybox.local` |
| `api` | `127.0.0.1:5000` | `https://api.pybox.local` |
| `pgadmin` | `127.0.0.1:5050` | `https://db-manager.pybox.local` |
| `database` (Postgres) | `127.0.0.1:5432` | — |

Los dominios `*.pybox.local` requieren resolverlos a `127.0.0.1` (`/etc/hosts` o similar) y usan certificados locales servidos por `server/nginx`.

## Levantar el entorno

```bash
cp .env.example .env   # completar credenciales/secretos reales
podman compose up -d --build
podman compose exec api alembic upgrade head
```

Restricción del entorno: **solo `podman compose ...`**, nunca `podman` a secas (hay otros contenedores en el host que no debe tocar el desarrollo de este proyecto). Tras reconstruir `api` o `client`, es necesario reiniciar `template-nginx` (el DNS interno queda obsoleto y produce 502).

## Tests

```bash
podman compose exec api pytest
podman compose exec client pnpm test
```
