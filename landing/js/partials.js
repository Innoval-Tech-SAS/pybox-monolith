// Inyecta el header (nav) y el footer compartidos entre páginas del landing.
// Vanilla JS puro, sin fetch ni build step: cada página solo necesita
// <body data-page="empresas|usuarios|contacto"> y los placeholders
// #nav-placeholder / #footer-placeholder. Debe cargarse (defer) antes de nav.js,
// que es quien engancha el comportamiento del menú hamburguesa una vez inyectado.
(function () {
  const YEAR = new Date().getFullYear();
  const ENV = window.ENV || {};
  const SIGN_IN_URL = ENV.SIGN_IN_URL || "https://app.pybox.local/admin/sign-in";
  const SIGN_UP_URL = ENV.SIGN_UP_URL || "https://app.pybox.local/admin/sign-up";

  const PAGE_NAV_LINKS = {
    empresas: [
      { href: "#audiencias", label: "Para quién es" },
      { href: "#beneficios", label: "Beneficios" },
      { href: "#servicios", label: "Servicios" },
    ],
    usuarios: [
      { href: "#beneficios", label: "Beneficios" },
      { href: "#como-funciona", label: "Cómo funciona" },
    ],
    contacto: [
      { href: "index.html#audiencias", label: "Para quién es" },
      { href: "index.html#beneficios", label: "Beneficios" },
      { href: "index.html#servicios", label: "Servicios" },
    ],
  };

  const PAGE_FOOTER_COLUMNS = {
    empresas: [
      { heading: "Servicios", items: ["Centralización de obligaciones y pagos", "Correo Certificado", "Certimail Admin", "Certimail Massive"] },
      { heading: "Valor para la operación", items: ["Más orden en la recuperación de cartera", "Mayor claridad para el usuario final", "Trazabilidad, evidencia y cumplimiento", "Reducción de costos y tiempos"] },
    ],
    usuarios: [
      { heading: "Servicios", items: ["Centralización de obligaciones y pagos", "Correo Certificado", "Certimail Admin", "Certimail Massive"] },
      { heading: "Para usuarios", items: ["Consulta tus obligaciones", "Recordatorios preventivos", "Calendario de pagos", "Atención más clara"] },
    ],
    contacto: [
      { heading: "Servicios", items: ["Centralización de obligaciones y pagos", "Correo Certificado", "Certimail Admin", "Certimail Massive"] },
      { heading: "Soporte", items: ["Formulario de contacto", "Radicación de PQRS", "Atención por correo certificado"] },
    ],
  };

  function anchorHref(page, anchor) {
    return page === "contacto" ? "#" + anchor : "contacto.html#" + anchor;
  }

  function buildNav(page) {
    const links = (PAGE_NAV_LINKS[page] || []).concat([
      { href: anchorHref(page, "contacto"), label: "Contacto" },
    ]);
    const desktopLinks = links.map((l) => `<a href="${l.href}" class="nav__link">${l.label}</a>`).join("");
    const mobileLinks = links.map((l) => `<a href="${l.href}" class="nav__mobile-link">${l.label}</a>`).join("");

    const isEmpresas = page === "empresas";
    const isUsuarios = page === "usuarios";
    const signupLabel = isUsuarios ? "Crear cuenta" : "Solicitar demo";

    return `
<nav class="nav" aria-label="Navegación principal">
  <div class="nav__inner container">
    <a href="index.html" class="nav__logo" aria-label="Pybox inicio">
      <span class="nav__logo-icon" aria-hidden="true">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><use href="#i-mail"/></svg>
      </span>
      <span class="nav__logo-name">Pybox</span>
    </a>
    <nav class="nav__links" aria-label="Secciones">${desktopLinks}</nav>
    <div class="nav__mode-toggle" role="group" aria-label="Modo">
      <a href="index.html" class="nav__mode-btn${isEmpresas ? " active" : ""}"${isEmpresas ? ' aria-current="page"' : ""}>Empresas</a>
      <a href="usuarios.html" class="nav__mode-btn${isUsuarios ? " active" : ""}"${isUsuarios ? ' aria-current="page"' : ""}>Usuarios</a>
    </div>
    <div class="nav__actions">
      <a href="${SIGN_IN_URL}" class="nav__link">Iniciar sesión</a>
      <a href="${SIGN_UP_URL}" class="btn btn--white">${signupLabel}</a>
    </div>
    <button id="nav-hamburger" class="nav__hamburger" aria-label="Menú" aria-expanded="false" aria-controls="nav-mobile-menu">
      <span class="nav__hamburger-line"></span>
      <span class="nav__hamburger-line"></span>
      <span class="nav__hamburger-line"></span>
    </button>
  </div>
  <div id="nav-mobile-menu" class="nav__mobile-menu container" role="menu">
    ${mobileLinks}
    <hr class="nav__mobile-divider"/>
    <a href="index.html" class="nav__mode-btn${isEmpresas ? " active" : ""}" style="width:fit-content">Empresas</a>
    <a href="usuarios.html" class="nav__mode-btn${isUsuarios ? " active" : ""}" style="width:fit-content">Usuarios</a>
    <hr class="nav__mobile-divider"/>
    <a href="${SIGN_IN_URL}" class="nav__mobile-link">Iniciar sesión</a>
    <a href="${SIGN_UP_URL}" class="btn btn--white" style="align-self:flex-start">${signupLabel}</a>
  </div>
</nav>`;
  }

  function buildFooter(page) {
    const columns = PAGE_FOOTER_COLUMNS[page] || PAGE_FOOTER_COLUMNS.empresas;
    const columnsHtml = columns
      .map(
        (col) => `
      <div>
        <div class="footer__heading">${col.heading}</div>
        <ul class="footer__list">${col.items.map((i) => `<li>${i}</li>`).join("")}</ul>
      </div>`
      )
      .join("");

    return `
<footer class="footer">
  <div class="container">
    <div class="footer__grid">
      <div>
        <div class="footer__logo">
          <span style="width:1.875rem;height:1.875rem;border-radius:.75rem;background:#6366f1;display:flex;align-items:center;justify-content:center;flex-shrink:0"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><use href="#i-mail"/></svg></span>
          <span class="footer__logo-name">Pybox</span>
        </div>
        <p class="footer__desc">Plataforma para centralizar obligaciones financieras, recuperar cartera y operar comunicaciones certificadas con evidencia.</p>
      </div>
      ${columnsHtml}
    </div>
    <div class="footer__bottom">
      <span>&copy; ${YEAR} Pybox. Todos los derechos reservados.</span>
      <a href="${anchorHref(page, "pqrs")}" class="footer__pqrs-link">Radicar PQRS</a>
      <span>Desarrollado por Innoval Tech</span>
    </div>
  </div>
</footer>`;
  }

  function applyEnvLinks() {
    document.querySelectorAll("[data-env-link]").forEach((el) => {
      el.setAttribute("href", el.getAttribute("data-env-link") === "sign-in" ? SIGN_IN_URL : SIGN_UP_URL);
    });
  }

  function render() {
    const page = document.body.getAttribute("data-page") || "empresas";
    const navPlaceholder = document.getElementById("nav-placeholder");
    const footerPlaceholder = document.getElementById("footer-placeholder");
    if (navPlaceholder) navPlaceholder.outerHTML = buildNav(page);
    if (footerPlaceholder) footerPlaceholder.outerHTML = buildFooter(page);
    applyEnvLinks();
  }

  render();
})();
