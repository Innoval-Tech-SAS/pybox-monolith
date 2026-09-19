FROM docker.io/library/nginx:alpine

ENV TZ=America/Bogota

# La config va dentro de la imagen; los certificados NO (llave privada): el compose monta
# /etc/letsencrypt (certbot del host) y el webroot /var/www/certbot.
COPY conf/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80 443
