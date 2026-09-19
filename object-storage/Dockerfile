FROM docker.io/chrislusf/seaweedfs:latest

ENV TZ=America/Bogota

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8333

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
