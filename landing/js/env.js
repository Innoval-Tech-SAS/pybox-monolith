// Valores por defecto para desarrollo local sin contenedor (ej. abrir el HTML
// directo o servirlo con un static server simple). En el contenedor, este
// archivo se regenera a partir de env.template.js con los valores reales del
// entorno (ver docker-entrypoint.sh).
window.ENV = {
  SIGN_IN_URL: "https://app.pybox.local/admin/sign-in",
  SIGN_UP_URL: "https://app.pybox.local/admin/sign-up",
};
