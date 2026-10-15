#!/usr/bin/env bash
# Despliegue de producción de pybox, instalado en el servidor como
# /usr/local/sbin/pybox-deploy (ver docs/ci-cd.md §2 para el setup de la llave SSH
# restringida y el sudoers que permite al usuario `deploy` ejecutar SOLO este script).
#
# A diferencia de credits-manager (Laravel), pybox no tiene un comando de respaldo
# propio ni un modo de mantenimiento (`artisan down`/`up`): el respaldo se hace con
# `pg_dump` directo y, si la migración falla, el script simplemente se detiene SIN
# recrear los contenedores de la app -- la versión vieja sigue respondiendo en vez
# de quedar caída a propósito. Es una estrategia distinta (menos ventana de downtime
# forzado) pero igual de segura: nunca se recrea un contenedor con código nuevo si
# la migración de su propia versión no pasó primero.
set -euo pipefail

REPO_DIR="/root/my-repositories/pybox-monolith"
BACKUP_DIR="/var/backups/pybox"
STATE_FILE="/var/lib/pybox/desplegado"
KEEP_IMAGES=5
# Nombre del proyecto compose con el que corre el stack en vivo (el de la carpeta del
# checkout). Si no coincide, compose crea un stack paralelo en otra red, sin acceso a la base.
PROJECT="pybox-monolith"
# Dominio provisional del cliente mientras app.pybox.co no tenga DNS.
CLIENT_URL="https://dev.pybox.co/"

SHA="${1:-}"
if ! [[ "$SHA" =~ ^[0-9a-f]{40}$ ]]; then
  echo "Se esperaba el SHA completo (40 caracteres hexadecimales) como único argumento." >&2
  exit 1
fi

cd "$REPO_DIR"

echo "==> git fetch"
git fetch origin main

REMOTE_SHA="$(git rev-parse origin/main)"
if [ "$SHA" != "$REMOTE_SHA" ]; then
  echo "SHA $SHA ya no es origin/main ($REMOTE_SHA) -- hubo un merge posterior, ese despliegue se encarga. Saliendo sin hacer nada."
  exit 0
fi

echo "==> git merge --ff-only"
git merge --ff-only origin/main

# El .env no se hace `source`: es formato dotenv, no bash (valores con espacios sin comillas
# se ejecutarían como comandos). Usuario y base se toman del entorno del propio contenedor.
echo "==> Respaldo previo (pg_dump)"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/pre-deploy-${SHA}.sql.gz"
if ! podman compose -p "$PROJECT" exec -T database \
    sh -c 'PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip > "$BACKUP_FILE"; then
  echo "El respaldo falló -- abortando sin tocar contenedores." >&2
  rm -f "$BACKUP_FILE"
  exit 1
fi
echo "Respaldo en $BACKUP_FILE"

echo "==> podman compose build"
podman compose -p "$PROJECT" build api client landing nginx

# podman-compose nombra las imágenes construidas localhost/<proyecto>_<servicio>:latest.
echo "==> Etiquetar imágenes con el SHA (para poder revertir)"
for servicio in api client landing nginx; do
  podman tag "localhost/${PROJECT}_${servicio}:latest" "pybox-${servicio}:${SHA}"
done

echo "==> Migrar (alembic upgrade head, con la imagen nueva de api, sin tocar el contenedor en vivo)"
if ! podman compose -p "$PROJECT" run -T --rm api alembic upgrade head; then
  echo "La migración falló -- los contenedores en producción NO se recrean (siguen corriendo la versión anterior)." >&2
  echo "Restaura con: gunzip -c $BACKUP_FILE | podman compose -p $PROJECT exec -T database sh -c 'PGPASSWORD=\"\$POSTGRES_PASSWORD\" psql -U \"\$POSTGRES_USER\" \"\$POSTGRES_DB\"'" >&2
  exit 1
fi

echo "==> Recrear solo los servicios de la aplicación (database/redis/storage no se tocan)"
podman compose -p "$PROJECT" up -d --force-recreate --no-deps api client landing nginx

echo "==> Verificación de salud"
if ! curl -fsS "https://api.pybox.co/" -o /dev/null; then
  echo "La API no respondió 200 en /. Revisar logs: podman compose -p $PROJECT logs api" >&2
  exit 1
fi
if ! curl -fsS "$CLIENT_URL" -o /dev/null; then
  echo "El cliente no respondió 200. Revisar logs: podman compose -p $PROJECT logs client nginx" >&2
  exit 1
fi

mkdir -p "$(dirname "$STATE_FILE")"
echo "$SHA" > "$STATE_FILE"

echo "==> Conservando solo las últimas $KEEP_IMAGES imágenes por servicio"
# Se borra por etiqueta y sin -f: si la imagen sigue en uso o tiene otra etiqueta (un servicio
# sin cambios entre despliegues comparte ID), rmi solo quita la etiqueta o falla sin tocar
# el contenedor en ejecución. `podman images` ya lista de la más nueva a la más vieja.
for servicio in api client landing nginx; do
  podman images "pybox-${servicio}" --format "{{.Repository}}:{{.Tag}}" \
    | grep -v ':latest$' \
    | tail -n "+$((KEEP_IMAGES + 1))" \
    | xargs -r podman rmi || true
done

echo "Despliegue de $SHA completo."
