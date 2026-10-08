// Alterna entre paneles [data-tab-panel] controlados por botones [data-tab].
// Solo un panel visible a la vez (vía atributo "hidden"). Sincroniza con el
// hash de la URL para que enlaces externos (ej. footer "Radicar PQRS") abran
// directamente en el panel correcto.
(function () {
  function initTabs() {
    const tabs = Array.prototype.slice.call(document.querySelectorAll("[data-tab]"));
    const panels = Array.prototype.slice.call(document.querySelectorAll("[data-tab-panel]"));
    if (!tabs.length || !panels.length) return;

    function activate(name, updateHash) {
      tabs.forEach(function (tab) {
        tab.setAttribute("aria-selected", String(tab.dataset.tab === name));
      });
      panels.forEach(function (panel) {
        panel.hidden = panel.dataset.tabPanel !== name;
      });
      if (updateHash) history.replaceState(null, "", "#" + name);
    }

    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        activate(tab.dataset.tab, true);
      });
    });

    const requested = (location.hash || "").slice(1);
    const isValid = tabs.some(function (tab) { return tab.dataset.tab === requested; });
    activate(isValid ? requested : tabs[0].dataset.tab, false);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTabs);
  } else {
    initTabs();
  }
})();
