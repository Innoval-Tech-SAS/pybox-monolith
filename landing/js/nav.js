// Menú mobile — toggle del hamburger
(function () {
  const hamburger = document.getElementById("nav-hamburger");
  const mobileMenu = document.getElementById("nav-mobile-menu");

  if (!hamburger || !mobileMenu) return;

  hamburger.addEventListener("click", function () {
    const isOpen = mobileMenu.classList.toggle("is-open");
    hamburger.setAttribute("aria-expanded", String(isOpen));
  });

  // Cerrar menú al hacer clic en un enlace interno
  mobileMenu.querySelectorAll("a").forEach(function (link) {
    link.addEventListener("click", function () {
      mobileMenu.classList.remove("is-open");
      hamburger.setAttribute("aria-expanded", "false");
    });
  });
})();
