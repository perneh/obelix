/**
 * Top navigation with ASTERIX / Link 16 dropdown menus.
 */

const PANELS = {
  asterix: {
    message: "tab-asterix-message",
    scenario: "tab-asterix-scenario",
    library: "tab-asterix-library",
  },
  link16: {
    message: "tab-link16-message",
    scenario: "tab-link16-scenario",
    library: "tab-link16-library",
  },
};

const PROTOCOL_LABELS = {
  asterix: "ASTERIX",
  link16: "Link 16",
};

const SUBTAB_LABELS = {
  message: "Message Editor",
  scenario: "Scenario Builder",
  library: "Configurations & Scenarios",
};

let currentProtocol = "asterix";
let currentSubtab = "message";
let initialized = false;

const listeners = [];

export function onNavigate(listener) {
  listeners.push(listener);
}

function updateToggleLabels(protocol, subtab) {
  document.querySelectorAll(".nav-dropdown").forEach((dropdown) => {
    const toggle = dropdown.querySelector(".nav-dropdown-toggle");
    if (!toggle) return;

    const dropdownProtocol = dropdown.dataset.protocol;
    const protocolLabel = PROTOCOL_LABELS[dropdownProtocol] || dropdownProtocol;

    if (dropdownProtocol === protocol) {
      toggle.textContent = `${protocolLabel} · ${SUBTAB_LABELS[subtab]}`;
    } else {
      toggle.textContent = protocolLabel;
    }
  });
}

export function navigateTo(protocol, subtab) {
  if (!PANELS[protocol]?.[subtab]) return;

  currentProtocol = protocol;
  currentSubtab = subtab;

  document.querySelectorAll(".nav-dropdown").forEach((dropdown) => {
    dropdown.classList.toggle("active", dropdown.dataset.protocol === protocol);
  });

  document.querySelectorAll(".nav-dropdown-item").forEach((item) => {
    const match =
      item.dataset.protocol === protocol && item.dataset.subtab === subtab;
    item.classList.toggle("active", match);
  });

  document.querySelectorAll(".panel").forEach((panel) => panel.classList.remove("active"));
  const panelId = PANELS[protocol][subtab];
  document.getElementById(panelId)?.classList.add("active");

  updateToggleLabels(protocol, subtab);
  closeAllDropdowns();
  listeners.forEach((fn) => fn({ protocol, subtab }));
}

function openDropdown(dropdown) {
  closeAllDropdowns();
  dropdown.classList.add("is-open");
  dropdown.querySelector(".nav-dropdown-menu")?.removeAttribute("hidden");
  dropdown.querySelector(".nav-dropdown-toggle")?.setAttribute("aria-expanded", "true");
}

function closeAllDropdowns() {
  document.querySelectorAll(".nav-dropdown").forEach((dropdown) => {
    dropdown.classList.remove("is-open");
    dropdown.querySelector(".nav-dropdown-menu")?.setAttribute("hidden", "");
    dropdown.querySelector(".nav-dropdown-toggle")?.setAttribute("aria-expanded", "false");
  });
}

export function initNavigation() {
  if (initialized) return;
  initialized = true;

  const nav = document.querySelector(".top-nav");
  if (!nav) return;

  nav.addEventListener("click", (event) => {
    const item = event.target.closest(".nav-dropdown-item");
    if (item) {
      event.preventDefault();
      event.stopPropagation();
      navigateTo(item.dataset.protocol, item.dataset.subtab);
      return;
    }

    const toggle = event.target.closest(".nav-dropdown-toggle");
    if (toggle) {
      event.preventDefault();
      event.stopPropagation();
      const dropdown = toggle.closest(".nav-dropdown");
      if (!dropdown) return;
      if (dropdown.classList.contains("is-open")) {
        closeAllDropdowns();
      } else {
        openDropdown(dropdown);
      }
    }
  });

  document.addEventListener("click", (event) => {
    if (event.target.closest(".nav-dropdown")) return;
    closeAllDropdowns();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeAllDropdowns();
  });

  navigateTo("asterix", "message");
}

export function currentView() {
  return { protocol: currentProtocol, subtab: currentSubtab };
}

export { SUBTAB_LABELS };

function bootNavigation() {
  initNavigation();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bootNavigation);
} else {
  // Defer until app.js / link16.js have registered onNavigate listeners.
  queueMicrotask(bootNavigation);
}
