// Plantilla procesada con envsubst por docker-entrypoint.sh al iniciar el
// contenedor, generando js/env.js con los valores reales de LANDING_SIGN_IN_URL
// y LANDING_SIGN_UP_URL definidos en el .env raíz / docker-compose.
window.ENV = {
  SIGN_IN_URL: "${LANDING_SIGN_IN_URL}",
  SIGN_UP_URL: "${LANDING_SIGN_UP_URL}",
};
