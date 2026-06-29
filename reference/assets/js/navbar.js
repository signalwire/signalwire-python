/* =============================================================================
   Fern navbar behaviour for the injected header (no iframe).
   Ported and trimmed from the SDK-docs POC (assets/js/app.js):
     - dropdown open/close + anchored positioning (product / language / support / theme)
     - theme toggle drives Material's own color scheme (default <-> slate)
   Out of scope for the pilot (different origin from signalwire.com):
     - cross-origin localStorage["theme"] sync with the Fern docs site
     - iframe theme bridging to other generators
   ============================================================================= */
(function () {
  "use strict";

  var CHECK_SVG =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"></path></svg>';

  /* --- Theme: drive Material's palette toggle ------------------------------- */
  // Material persists its own scheme in localStorage under "__palette" and
  // exposes a hidden radio (input[data-md-color-scheme]) per palette. We just
  // click it, so Material owns persistence and the rest of its UI stays in sync.
  function currentScheme() {
    return document.body.getAttribute("data-md-color-scheme") || "default";
  }
  function setScheme(scheme) {
    var inputs = document.querySelectorAll('input[name="__palette"]');
    for (var i = 0; i < inputs.length; i++) {
      if (inputs[i].getAttribute("data-md-color-scheme") === scheme) {
        inputs[i].click();
        return true;
      }
    }
    // Fallback if Material's palette toggle isn't configured: set attrs directly.
    document.body.setAttribute("data-md-color-scheme", scheme);
    return false;
  }
  function syncThemeUI() {
    var dark = currentScheme() === "slate";
    var sun = document.getElementById("theme-icon-sun");
    var moon = document.getElementById("theme-icon-moon");
    if (sun) sun.hidden = dark;
    if (moon) moon.hidden = !dark;
    var pref = dark ? "dark" : "light";
    var items = document.querySelectorAll("#theme-panel [data-theme-pref]");
    for (var i = 0; i < items.length; i++) {
      var chk = items[i].querySelector("[data-check]");
      if (chk) chk.innerHTML = items[i].getAttribute("data-theme-pref") === pref ? CHECK_SVG : "";
    }
  }

  /* --- Dropdowns ------------------------------------------------------------ */
  var dropdowns = [];
  function registerDropdown(triggerId, panelId, opts) {
    opts = opts || {};
    var align = opts.align || "start";
    var offset = opts.offset != null ? opts.offset : 8;
    var trigger = document.getElementById(triggerId);
    var panel = document.getElementById(panelId);
    if (!trigger || !panel) return null;

    function position() {
      var r = trigger.getBoundingClientRect();
      panel.style.top = r.bottom + offset + "px";
      if (align === "end") {
        panel.style.right = Math.max(8, window.innerWidth - r.right) + "px";
        panel.style.left = "auto";
      } else if (align === "center") {
        var w = panel.offsetWidth;
        var c = r.left + r.width / 2 - w / 2;
        panel.style.left = Math.min(Math.max(8, c), window.innerWidth - w - 8) + "px";
        panel.style.right = "auto";
      } else {
        var width = panel.offsetWidth;
        panel.style.left = Math.min(r.left, Math.max(8, window.innerWidth - width - 8)) + "px";
        panel.style.right = "auto";
      }
    }
    var dd = {
      isOpen: function () { return panel.getAttribute("data-state") === "open"; },
      set: function (open) {
        panel.setAttribute("data-state", open ? "open" : "closed");
        trigger.setAttribute("data-state", open ? "open" : "closed");
        trigger.setAttribute("aria-expanded", String(open));
        if (open) position();
      },
    };
    trigger.addEventListener("click", function (e) {
      e.stopPropagation();
      var willOpen = !dd.isOpen();
      closeAll();
      dd.set(willOpen);
    });
    dropdowns.push(dd);
    return dd;
  }
  function closeAll() { for (var i = 0; i < dropdowns.length; i++) dropdowns[i].set(false); }

  document.addEventListener("click", function (e) {
    if (!e.target.closest(".fern-dropdown, [data-testid='product-dropdown-content']")) closeAll();
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeAll(); });
  window.addEventListener("resize", closeAll);

  /* --- Init ----------------------------------------------------------------- */
  function init() {
    registerDropdown("product-trigger", "product-panel", { align: "start" });
    registerDropdown("lang-trigger", "lang-panel", { align: "center" });
    registerDropdown("support-trigger", "support-panel", { align: "end" });
    registerDropdown("theme-trigger", "theme-panel", { align: "end" });

    var themeItems = document.querySelectorAll("#theme-panel [data-theme-pref]");
    for (var i = 0; i < themeItems.length; i++) {
      themeItems[i].addEventListener("click", function () {
        closeAll();
        var pref = this.getAttribute("data-theme-pref");
        // System resolves to the OS preference; pilot maps it to light/dark now.
        if (pref === "system") {
          pref = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
        }
        setScheme(pref === "dark" ? "slate" : "default");
        setTimeout(syncThemeUI, 0);
      });
    }
    // Header sun/moon button = quick toggle.
    var themeTrigger = document.getElementById("theme-trigger");
    syncThemeUI();
    // Material re-applies the scheme asynchronously; observe to keep icons in sync.
    var obs = new MutationObserver(syncThemeUI);
    obs.observe(document.body, { attributes: true, attributeFilter: ["data-md-color-scheme"] });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
