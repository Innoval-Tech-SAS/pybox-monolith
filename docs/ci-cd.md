# CI/CD — pybox

## 1. Cómo funciona

```
PR hacia main ──► CI (.github/workflows/ci.yml)
                    ├─ API: black + pylint + pytest (Postgres 17 + storage reales)
                    ├─ Migraciones: todas, desde cero, en Postgres 17 (alembic upgrade head)
                    ├─ Cliente: lint + Vitest + build
                    └─ Imágenes de producción: api, client, landing y nginx construyen
                  Branch protection: sin los 4 checks en verde no se puede hacer merge.

merge a main ──► CI otra vez sobre el commit de main
             ──► Deploy (.github/workflows/deploy.yml)
                    ├─ environment `PROD` (secretos de despliegue, solo rama main)
                    └─ SSH al servidor ──► scripts/deploy.sh <sha>    (automático, sin aprobación)
```

`scripts/deploy.sh` (instalado como `/usr/local/sbin/pybox-deploy`) hace, en el checkout
de producción:

1. Valida que el SHA sea el de `origin/main`. Si hubo un merge posterior, no hace nada: ese otro despliegue se encarga.
2. Hace `git merge --ff-only` en el checkout de producción.
3. **Respaldo previo** (`pg_dump` directo, comprimido en `/var/backups/pybox/`). Si falla, se detiene sin tocar los contenedores.
4. Ejecuta `podman compose build` y etiqueta las imágenes con el SHA para poder revertir.
5. Corre `alembic upgrade head` con la imagen nueva de `api` (`podman compose run --rm api ...`), **sin** recrear el contenedor en vivo todavía.
6. Si la migración falla, el script se detiene ahí: los contenedores en producción siguen corriendo la versión anterior (no hay modo mantenimiento tipo `artisan down`; en su lugar, simplemente nunca se llega a recrear nada con código que no migró bien).
7. Si la migración pasa, recrea solo los servicios de la aplicación (`--force-recreate --no-deps api client landing nginx`). La base, Redis y el storage no se reinician.
8. Comprueba que `https://api.pybox.co/` y `https://app.pybox.co/` respondan 200.
9. Guarda el SHA desplegado en `/var/lib/pybox/desplegado` y conserva las imágenes de los últimos 5 despliegues por servicio.

**Autorización de migraciones:** el despliegue es totalmente automático. **El merge a `main` es la autorización**: quien aprueba el PR debe revisar si trae migraciones (`api/alembic/versions/`) y si son compatibles hacia atrás.

> Diferencia deliberada con credits-manager: ahí Laravel pone la app en mantenimiento (`artisan down`) mientras migra. FastAPI/Alembic no tiene un equivalente nativo, así que aquí se invierte el orden: se migra con una imagen nueva que todavía NO está sirviendo tráfico, y solo se recrean los contenedores de la app si la migración ya pasó. El costo es que, durante el `run --rm api alembic upgrade head`, el contenedor viejo sigue respondiendo con el esquema anterior — aceptable mientras las migraciones del proyecto sigan siendo compatibles hacia atrás (columna nueva nullable, no un rename/drop en el mismo PR que el código que ya la usa).

---

## 2. Configuración inicial (una sola vez)

### 2.1. Servidor: usuario de despliegue

Como root en el servidor:

```bash
useradd --create-home --shell /bin/bash deploy

install -o root -g root -m 0755 /root/repositories/pybox-monolith/scripts/deploy.sh \
  /usr/local/sbin/pybox-deploy

echo 'deploy ALL=(root) NOPASSWD: /usr/local/sbin/pybox-deploy' > /etc/sudoers.d/pybox-deploy
chmod 440 /etc/sudoers.d/pybox-deploy
visudo -c
```

Cada vez que `scripts/deploy.sh` cambie en el repositorio, hay que repetir el `install`.

### 2.2. Llave SSH de GitHub

Como root, en el servidor:

```bash
ssh-keygen -t ed25519 -N '' -C 'github-actions-deploy' -f /root/deploy_key

install -o deploy -g deploy -m 700 -d /home/deploy/.ssh
printf 'restrict,command="sudo -n /usr/local/sbin/pybox-deploy \\"$SSH_ORIGINAL_COMMAND\\"" %s\n' \
  "$(cat /root/deploy_key.pub)" > /home/deploy/.ssh/authorized_keys
chown deploy:deploy /home/deploy/.ssh/authorized_keys
chmod 600 /home/deploy/.ssh/authorized_keys

ssh-keyscan -t ed25519 <IP_DEL_SERVIDOR>
```

Con `restrict,command=…` esa llave **solo** puede ejecutar `pybox-deploy`. Copia `/root/deploy_key`
(privada) a los secretos de GitHub (paso 2.3) y bórrala del servidor: `shred -u /root/deploy_key`.

### 2.3. Secretos en GitHub (Settings → Secrets and variables → Actions)

| Secreto | Valor |
|---|---|
| `DEPLOY_HOST` | IP o dominio del servidor |
| `DEPLOY_USER` | `deploy` |
| `DEPLOY_SSH_KEY` | contenido de `/root/deploy_key` (privada) |
| `DEPLOY_KNOWN_HOSTS` | salida de `ssh-keyscan` del paso 2.2 |

En organizaciones con plan Free, los secretos puestos en un **Environment** (en vez de en
los secretos del repo) no llegan a repositorios privados — usar los secretos del repo
directamente si `deploy.yml` falla con "Secretos vacíos" aunque estén configurados en `PROD`.

### 2.4. Servidor: lectura del repositorio sin contraseña

El script hace `git fetch` como root, así que necesita su propia deploy key de solo lectura
hacia el repositorio (`ssh-keygen` + entrada en `~/.ssh/config` + deploy key agregada en
GitHub → repo → Settings → Deploy keys, solo lectura).

---

## 3. Variables de entorno obligatorias al importar

`api/.env.example` documenta cada una. Varias (`AUTH_TOKEN_SECRET`, `MP_*_MX`, `NRS360_*`,
`WHATSAPP_CLOUD_*`, etc.) se cargan a nivel de módulo al importar la app: sin ellas, ni
`uvicorn` ni `pytest` arrancan. `ci.yml` las fija a valores dummy no-secretos solo para que
la API importe en el pipeline; producción usa el `.env` real del servidor, nunca estos valores.
