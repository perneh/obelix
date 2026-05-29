/** Built-in scenario templates and editor helpers. */

export const DEFAULT_TEMPLATE_PARAMS = {
  tick_interval_ms: 2000,
  ticks: 60,
  jas_track_number: 101,
  mig_track_number: 201,
  jas_mode3a: 7777,
  mig_mode3a: 7770,
  jas_flight_level: 350,
  mig_flight_level: 410,
  loop_count: 1,
  host: "host.docker.internal",
  port: 8600,
};

export function readTemplateParamsFromForm() {
  return {
    tick_interval_ms: parseInt(document.getElementById("tpl-tick-interval").value, 10),
    ticks: parseInt(document.getElementById("tpl-ticks").value, 10),
    jas_track_number: parseInt(document.getElementById("tpl-jas-track").value, 10),
    mig_track_number: parseInt(document.getElementById("tpl-mig-track").value, 10),
    jas_mode3a: parseInt(document.getElementById("tpl-jas-mode3a").value, 10),
    mig_mode3a: parseInt(document.getElementById("tpl-mig-mode3a").value, 10),
    jas_flight_level: parseFloat(document.getElementById("tpl-jas-fl").value),
    mig_flight_level: parseFloat(document.getElementById("tpl-mig-fl").value),
    loop_count: parseInt(document.getElementById("scenario-loops").value, 10),
    host: document.getElementById("scenario-host").value,
    port: parseInt(document.getElementById("scenario-port").value, 10),
    scenario_name: document.getElementById("scenario-name").value || null,
  };
}

export function applyScenarioToEditor(scenario) {
  document.getElementById("scenario-name").value = scenario.name || "";
  document.getElementById("scenario-loops").value = scenario.loop_count ?? 1;
  document.getElementById("scenario-interval").value = scenario.interval_ms ?? 1000;
  document.getElementById("scenario-host").value = scenario.transport?.host ?? "host.docker.internal";
  document.getElementById("scenario-port").value = scenario.transport?.port ?? 8600;
  document.getElementById("scenario-protocol").value = scenario.transport?.protocol ?? "udp";
}

export function countScenarioMessages(steps) {
  return steps.reduce((total, step) => {
    if (step.motion?.enabled) {
      return total + (step.motion.ticks || 1);
    }
    return total + (step.repeat || 1);
  }, 0);
}

export function renderTemplateCatalog(catalog, onSelect) {
  const container = document.getElementById("template-catalog");
  container.innerHTML = catalog
    .map(
      (t) =>
        `<article class="template-card" data-template-id="${t.id}">
          <h4>${t.name}</h4>
          <p class="muted">${t.description}</p>
          <p class="template-meta"><strong>${t.aircraft}</strong> · ${t.route}</p>
          <button type="button" class="btn secondary btn-sm" data-load-template="${t.id}">Load template</button>
        </article>`
    )
    .join("");

  container.querySelectorAll("[data-load-template]").forEach((btn) => {
    btn.addEventListener("click", () => onSelect(btn.dataset.loadTemplate));
  });
}
