# Pybox Landing

Sitio de marketing/SEO de Pybox. HTML5 + CSS3 + JS vanilla, **sin build ni framework** — se sirve tal cual está en el repo.

Ver también el [README del proyecto](../README.md) y las reglas de arquitectura en [CLAUDE.md](../CLAUDE.md). Para cualquier pieza visual nueva bajo `landing/**`, la skill obligatoria es `frontend-design` (no `tailadmin-design-language`, que solo aplica dentro de `client/src/**`).

## Estructura

```
index.html        página principal
contacto.html      formulario/información de contacto
usuarios.html      landing orientada a usuarios finales (deudores)
not-found.html     página de error 404
css/
  base.css          reset, tipografía, variables de diseño
  components.css     componentes reutilizables (nav, cards, botones, etc.)
js/
  env.js             variables de entorno resueltas en runtime (generado, no editar a mano)
  env.template.js     plantilla con placeholders `${LANDING_SIGN_IN_URL}` / `${LANDING_SIGN_UP_URL}`
  nav.js, partials.js, tabs.js   interactividad de la página (nav, includes de HTML, tabs)
```

## Variables de entorno en runtime

El sitio no tiene build step, pero sí necesita dos URLs configurables por entorno (los links de "Iniciar sesión" / "Registrarse" al `client`). `docker-entrypoint.sh` corre al arrancar el contenedor nginx y sustituye los placeholders de `js/env.template.js` con `LANDING_SIGN_IN_URL` y `LANDING_SIGN_UP_URL` del entorno, generando `js/env.js`:

```bash
LANDING_SIGN_IN_URL="https://app.pybox.local/admin/sign-in"
LANDING_SIGN_UP_URL="https://app.pybox.local/admin/sign-up"
```

Nunca se edita `js/env.js` directamente — es un archivo generado y se sobreescribe en cada arranque del contenedor.

## Servido por nginx

`nginx.conf` sirve los archivos estáticos con cache de 1h para assets (`css|js|png|jpg|jpeg|gif|ico|svg|woff2?`) y redirige 404 a `not-found.html`. En el reverse proxy (`server/nginx`), `landing` responde en el dominio raíz `https://pybox.local`.

## Desarrollo local (Podman)

Como no hay build, para iterar rápido basta con abrir los `.html` directo en el navegador (los links a `client` usarán las URLs de `js/env.js` como estén generadas). Para probar el flujo completo con nginx y las variables de entorno reales:

```bash
podman compose up -d --build landing
podman compose logs -f landing
```

Tras reconstruir la imagen de `landing`, reiniciar `template-nginx` si el DNS interno queda obsoleto (502).
