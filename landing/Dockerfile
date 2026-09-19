FROM nginx:alpine
COPY . /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY docker-entrypoint.sh /docker-entrypoint.d/40-landing-env.sh
RUN chmod +x /docker-entrypoint.d/40-landing-env.sh
