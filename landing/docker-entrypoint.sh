#!/bin/sh
# Se ejecuta automáticamente por la imagen oficial de nginx (scripts en
# /docker-entrypoint.d/ corren antes de arrancar nginx). Sustituye los
# placeholders de env.template.js con las variables de entorno reales del
# contenedor y sobreescribe js/env.js.
set -eu

export LANDING_SIGN_IN_URL="${LANDING_SIGN_IN_URL:-https://app.pybox.local/admin/sign-in}"
export LANDING_SIGN_UP_URL="${LANDING_SIGN_UP_URL:-https://app.pybox.local/admin/sign-up}"

envsubst '${LANDING_SIGN_IN_URL} ${LANDING_SIGN_UP_URL}' \
  < /usr/share/nginx/html/js/env.template.js \
  > /usr/share/nginx/html/js/env.js
