# Pybox Client

Frontend admin de Pybox: React 19 + TypeScript + Vite + Tailwind CSS v4, basado en el template [TailAdmin](https://react-demo.tailadmin.com/). Gestionado con `pnpm`.

Ver también el [README del proyecto](../README.md) y las reglas de arquitectura en [CLAUDE.md](../CLAUDE.md).

## Stack

- **React 19 + TypeScript + Vite**, SWC para Fast Refresh.
- **Tailwind CSS v4**.
- **React Router 7** — rutas declaradas en `src/router.tsx` (`noAuthRouter` / `authRouter`), todas las páginas cargadas con `lazy()`.
- **ApexCharts**, **FullCalendar**, **@xyflow/react** (diseñador de flujos IVR y builder de campañas), **react-email-editor** (editor de plantillas), **react-dnd**, **driver.js** (tours de producto).
- **Vitest** + Testing Library para tests.

## Estructura (`src/`)

Organizado por dominio de negocio, no por tipo de archivo — cada carpeta refleja una sección del producto y agrupa sus propios `components/`, `hooks/`, `pages/`, `types/`, `utils/`:

```
auth/                 login, sign-up, forgot/change password
onboarding/           alta de organización, primer acceso
companies/             organizaciones, portafolios, deudores, pagos, historial, settings, comunicaciones
credits/               créditos y estados de cuenta del propio usuario (autoservicio)
billing/               facturación admin (pasarelas, facturas)
users/                  gestión de usuarios y permisos
campaigns/, templates/  campañas de mensajería y plantillas
bulk-send/              envío masivo por CSV
segments/, reports/     segmentación de cartera y reportería
ivr/                    diseñador de flujos IVR y monitor/reportes de ejecución
whatsapp/               chats en vivo de WhatsApp
chat/                   chat interno (WebSocket)
databases/              explorador/editor de esquemas de base de datos
provider-credentials/   credenciales de proveedores por organización
notifications/, support/, profile/, home/  notificaciones, tickets de soporte, perfil, dashboard
ui/                     componentes, layouts, íconos y utilidades compartidas entre dominios
```

`ui/` es la base común (layout con sidebar/header, componentes de TailAdmin adaptados, iconos, contexts globales) — cualquier UI nueva reutiliza lo que ya existe ahí antes de crear estilos desde cero.

## Diseño visual

El lenguaje visual sigue **estrictamente** el de TailAdmin: composición, densidad, jerarquía tipográfica, iconografía y estilo de cards/charts/badges se reproducen, no se reinventan, aunque los datos y el dominio sean completamente distintos a los de la demo. Ver skills `tailadmin-react` y `tailadmin-design-language` en [CLAUDE.md](../CLAUDE.md) — obligatorias para cualquier cambio bajo `src/**`. (`frontend-design` es solo para `landing/`, no aplica aquí.)

## Scripts

```bash
pnpm dev        # servidor de desarrollo (Vite, --host)
pnpm build      # type-check (tsc -b) + build de producción
pnpm lint       # eslint
pnpm test       # vitest run
pnpm test:watch # vitest en modo watch
```

## Desarrollo local (Podman)

El host no requiere Node/npm instalado — todo corre en contenedores. Uso restringido a `podman compose ...` (nunca `podman` a secas).

```bash
podman compose up -d --build client
podman compose logs -f client
```

Tras reconstruir la imagen de `client`, reiniciar `template-nginx` (el DNS interno queda obsoleto y produce 502). En local, la app se sirve en `https://app.pybox.local` (vía `server/nginx`) o directo en `http://127.0.0.1:8083`.

## Tests

```bash
podman compose exec client pnpm test
```

Los tests viven en `tests/`, reflejando la ruta de `src/` — nunca junto al código fuente.
