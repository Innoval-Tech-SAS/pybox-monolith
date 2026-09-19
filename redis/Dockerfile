FROM docker.io/library/redis:7-alpine

ENV TZ=America/Bogota

EXPOSE 6379

# La contraseña llega en REDIS_PASSWORD (la inyecta docker-compose.yaml desde el .env
# raíz) y se expande al arrancar, así no queda guardada en la imagen.
# Se pasa por el docker-entrypoint.sh original de la imagen (no directo a redis-server ni
# con `sh` como primer argumento): ese script es el que ajusta permisos de /data y baja
# a redis a un usuario sin privilegios, y solo lo hace si el primer argumento es
# `redis-server`.
ENTRYPOINT ["sh", "-c", "exec docker-entrypoint.sh redis-server --requirepass \"$REDIS_PASSWORD\" --appendonly yes"]
