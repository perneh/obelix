/**
 * Obelix Link 16 — message editor, scenario builder, configurations.
 */

import { renderMarkdown } from "./markdown.js";
import { formatApiError } from "./scenario-io.js";
import { navigateTo, onNavigate } from "./navigation.js";

const API = "/api/link16";

const state = {
  messages: [],
  families: {},
  familyFilter: "all",
  selectedSeries: null,
  messageDef: null,
  fieldValues: {},
  help: null,
  helpOpen: false,
  scenarioSteps: [],
  activeScenarioId: null,
  scenarioRunning: false,
  scenarioPaused: false,
  statusPollTimer: null,
};

function jSeriesSlug(jSeries) {
  return jSeries.replace(".", "-");
}

async function api(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(formatApiError(err));
  }
  return res.json();
}

function buildDefaults(fields) {
  const values = {};
  for (const field of fields) {
    if (field.type === "compound") {
      values[field.id] = {};
      for (const sub of field.fields) {
        values[field.id][sub.id] = sub.default;
      }
    } else {
      values[field.id] = field.default;
    }
  }
  return values;
}

function renderField(field, parentId = null) {
  const fieldKey = parentId ? `${parentId}.${field.id}` : field.id;

  if (field.type === "compound") {
    return `
      <div class="field-group">
        <label>${field.label}</label>
        ${field.description ? `<div class="field-desc">${field.description}</div>` : ""}
        <div class="compound-fields">
          ${field.fields.map((sub) => renderField(sub, field.id)).join("")}
        </div>
      </div>`;
  }

  const value = parentId
    ? state.fieldValues[parentId]?.[field.id]
    : state.fieldValues[field.id];

  if (field.type === "enum") {
    return `
      <div class="field-group">
        <label for="l16-${fieldKey}">${field.label}</label>
        ${field.description ? `<div class="field-desc">${field.description}</div>` : ""}
        <select id="l16-${fieldKey}" data-field="${fieldKey}">
          ${field.options
            .map(
              (opt) =>
                `<option value="${opt.value}" ${String(opt.value) === String(value) ? "selected" : ""}>${opt.label}</option>`
            )
            .join("")}
        </select>
      </div>`;
  }

  if (field.type === "string") {
    return `
      <div class="field-group">
        <label for="l16-${fieldKey}">${field.label}</label>
        ${field.description ? `<div class="field-desc">${field.description}</div>` : ""}
        <input type="text" id="l16-${fieldKey}" data-field="${fieldKey}" value="${value ?? ""}">
      </div>`;
  }

  const step = field.type === "float" ? "any" : "1";
  const min = field.min !== undefined ? `min="${field.min}"` : "";
  const max = field.max !== undefined ? `max="${field.max}"` : "";
  const unit = field.unit ? ` (${field.unit})` : "";

  return `
    <div class="field-group">
      <label for="l16-${fieldKey}">${field.label}${unit}</label>
      ${field.description ? `<div class="field-desc">${field.description}</div>` : ""}
      <input type="number" id="l16-${fieldKey}" data-field="${fieldKey}"
        value="${value}" step="${step}" ${min} ${max}>
    </div>`;
}

function renderWordLayout(messageDef) {
  if (!messageDef.word_layout?.length) return "";
  const rows = messageDef.word_layout
    .map(
      (entry) => `<tr>
        <td>${entry.frn}</td>
        <td>${entry.word}</td>
        <td>${entry.name}</td>
        <td>${entry.length_bits}</td>
        <td>${entry.field_id ? `<code>${entry.field_id}</code>` : "—"}</td>
      </tr>`
    )
    .join("");

  return `
    <div class="uap-panel">
      <h3>Word layout</h3>
      <p class="muted section-desc">${messageDef.j_series} · NPG ${messageDef.npg} · ${messageDef.edition}</p>
      <div class="uap-table-wrap">
        <table class="uap-table">
          <thead>
            <tr><th>FRN</th><th>Word</th><th>Field</th><th>Bits</th><th>Form</th></tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </div>`;
}

function renderForm() {
  const form = document.getElementById("link16-form");
  if (!state.messageDef) {
    form.innerHTML = "";
    return;
  }
  form.innerHTML =
    renderWordLayout(state.messageDef) +
    state.messageDef.fields.map((field) => renderField(field)).join("");

  form.querySelectorAll("[data-field]").forEach((el) => {
    el.addEventListener("change", onFieldChange);
    el.addEventListener("input", onFieldChange);
  });
}

function findFieldDef(parentId, subId) {
  const parent = state.messageDef.fields.find((f) => f.id === parentId);
  return parent?.fields?.find((f) => f.id === subId);
}

function parseFieldValue(raw, fieldDef) {
  if (!fieldDef) return raw;
  if (fieldDef.type === "string") return raw;
  if (fieldDef.type === "float") return parseFloat(raw);
  if (fieldDef.type === "enum") {
    const num = parseInt(raw, 10);
    return Number.isNaN(num) ? raw : num;
  }
  return parseInt(raw, 10);
}

function onFieldChange(e) {
  const key = e.target.dataset.field;
  const parts = key.split(".");
  if (parts.length === 2) {
    if (!state.fieldValues[parts[0]]) state.fieldValues[parts[0]] = {};
    state.fieldValues[parts[0]][parts[1]] = parseFieldValue(
      e.target.value,
      findFieldDef(parts[0], parts[1])
    );
  } else {
    const fieldDef = state.messageDef.fields.find((f) => f.id === key);
    state.fieldValues[key] = parseFieldValue(e.target.value, fieldDef);
  }
}

function getCurrentMessage() {
  return {
    j_series: state.selectedSeries,
    fields: structuredClone(state.fieldValues),
  };
}

function renderMessageList() {
  const list = document.getElementById("link16-message-list");
  const filtered =
    state.familyFilter === "all"
      ? state.messages
      : state.messages.filter((m) => m.family === state.familyFilter);

  list.innerHTML = filtered
    .map(
      (msg) =>
        `<li data-series="${msg.j_series}" class="${msg.j_series === state.selectedSeries ? "active" : ""}">
          <span class="cat-num">${msg.j_series}</span>${msg.name}
        </li>`
    )
    .join("");

  list.querySelectorAll("li").forEach((li) => {
    li.addEventListener("click", () => selectMessage(li.dataset.series));
  });
}

function renderFamilyFilter() {
  const container = document.getElementById("link16-family-filter");
  const families = ["all", ...Object.keys(state.families).sort()];
  container.innerHTML = `
    <label>Family
      <select id="link16-family-select">
        ${families
          .map(
            (f) =>
              `<option value="${f}" ${f === state.familyFilter ? "selected" : ""}>${
                f === "all" ? "All families" : f
              }</option>`
          )
          .join("")}
      </select>
    </label>`;

  document.getElementById("link16-family-select")?.addEventListener("change", (e) => {
    state.familyFilter = e.target.value;
    renderMessageList();
  });
}

async function selectMessage(jSeries) {
  state.selectedSeries = jSeries;
  state.messageDef = await api(`/messages/${jSeriesSlug(jSeries)}`);
  state.fieldValues = buildDefaults(state.messageDef.fields);
  state.help = null;
  state.helpOpen = false;

  document.getElementById("link16-title").textContent =
    `${jSeries} – ${state.messageDef.name}`;
  document.getElementById("link16-description").textContent = state.messageDef.description;

  const helpBtn = document.getElementById("btn-link16-help");
  helpBtn.hidden = false;
  helpBtn.setAttribute("aria-expanded", "false");
  document.getElementById("link16-help-panel").classList.add("hidden");
  document.getElementById("link16-help-panel").innerHTML = "";
  document.getElementById("link16-hex-output").textContent = "—";

  renderMessageList();
  renderForm();
}

async function loadMessages() {
  state.messages = await api("/messages");
  state.families = await api("/families");
  renderFamilyFilter();
  renderMessageList();
  if (state.messages.length > 0) {
    await selectMessage(state.messages[0].j_series);
  }
}

document.getElementById("btn-link16-help")?.addEventListener("click", async () => {
  const panel = document.getElementById("link16-help-panel");
  const helpBtn = document.getElementById("btn-link16-help");

  if (state.helpOpen) {
    panel.classList.add("hidden");
    state.helpOpen = false;
    helpBtn.setAttribute("aria-expanded", "false");
    return;
  }

  try {
    helpBtn.disabled = true;
    if (!state.help) {
      state.help = await api(`/messages/${jSeriesSlug(state.selectedSeries)}/help`);
    }
    panel.innerHTML = `<article class="help-content">${renderMarkdown(state.help.content)}</article>`;
    panel.classList.remove("hidden");
    state.helpOpen = true;
    helpBtn.setAttribute("aria-expanded", "true");
  } catch (err) {
    panel.innerHTML = `<p class="status error">${err.message}</p>`;
    panel.classList.remove("hidden");
  } finally {
    helpBtn.disabled = false;
  }
});

document.getElementById("btn-link16-encode")?.addEventListener("click", async () => {
  try {
    const result = await api("/encode", {
      method: "POST",
      body: JSON.stringify({ message: getCurrentMessage() }),
    });
    document.getElementById("link16-hex-output").textContent =
      `${result.hex}\n(${result.length} bytes, ${result.j_series})`;
  } catch (err) {
    document.getElementById("link16-hex-output").textContent = `Error: ${err.message}`;
  }
});

document.getElementById("btn-link16-send")?.addEventListener("click", async () => {
  const statusEl = document.getElementById("link16-send-status");
  statusEl.textContent = "Sending…";
  statusEl.className = "status";

  try {
    const result = await api("/send", {
      method: "POST",
      body: JSON.stringify({
        message: getCurrentMessage(),
        host: document.getElementById("link16-send-host").value,
        port: parseInt(document.getElementById("link16-send-port").value, 10),
        protocol: document.getElementById("link16-send-protocol").value,
      }),
    });
    statusEl.textContent = `Sent ${result.bytes_sent} bytes to ${result.host}:${result.port} (${result.j_series})`;
    statusEl.className = "status success";
  } catch (err) {
    statusEl.textContent = err.message;
    statusEl.className = "status error";
  }
});

loadMessages().catch((err) => {
  document.getElementById("link16-description").textContent = `Failed to load Link 16 messages: ${err.message}`;
});

// --- Configurations ---

function slugify(name) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

async function saveLink16Configuration() {
  const name = prompt("Configuration name:");
  if (!name) return;
  const id = slugify(name);
  if (!id) return;

  try {
    await api("/configurations", {
      method: "POST",
      body: JSON.stringify({
        id,
        name,
        description: "",
        scope: "local",
        message: getCurrentMessage(),
      }),
    });
    alert(`Saved "${name}" to data/link16_configurations/`);
  } catch (err) {
    alert(`Failed to save: ${err.message}`);
  }
}

document.getElementById("btn-link16-save-local")?.addEventListener("click", saveLink16Configuration);

async function loadLink16Library() {
  const configurations = await api("/configurations");
  const scenarios = await api("/saved-scenarios");

  configurations.forEach((c) => {
    c.config_id =
      c.config_id || `${c.scope}:${jSeriesSlug(c.message.j_series)}:${c.id}`;
  });

  const filterSelect = document.getElementById("link16-config-series-filter");
  const currentFilter = filterSelect?.value ?? "";
  const seriesList = [...new Set(configurations.map((c) => c.message.j_series))].sort();
  if (filterSelect) {
    filterSelect.innerHTML =
      `<option value="">All J-messages</option>` +
      seriesList.map((s) => `<option value="${s}">${s}</option>`).join("");
    filterSelect.value = currentFilter;
    filterSelect.onchange = () => renderLink16ConfigurationList(configurations);
  }

  renderLink16ConfigurationList(configurations);

  const scenarioList = document.getElementById("link16-saved-scenario-list");
  if (scenarioList) {
    scenarioList.innerHTML = scenarios.length
      ? scenarios
          .map(
            (s) =>
              `<li>
                <span>${s.name} (${s.steps.length} steps)</span>
                <span class="item-actions">
                  <button data-link16-load-scenario="${s.id}">Load</button>
                  <button data-link16-delete-scenario="${s.id}">Delete</button>
                </span>
              </li>`
          )
          .join("")
      : "<li>No scenarios saved</li>";

    scenarioList.querySelectorAll("[data-link16-load-scenario]").forEach((btn) => {
      btn.addEventListener("click", () => loadLink16SavedScenario(btn.dataset.link16LoadScenario));
    });
    scenarioList.querySelectorAll("[data-link16-delete-scenario]").forEach((btn) => {
      btn.addEventListener("click", () => deleteLink16SavedScenario(btn.dataset.link16DeleteScenario));
    });
  }
}

function renderLink16ConfigurationList(configurations) {
  const filter = document.getElementById("link16-config-series-filter")?.value ?? "";
  const filtered = filter
    ? configurations.filter((c) => c.message.j_series === filter)
    : configurations;

  const list = document.getElementById("link16-configuration-list");
  if (!list) return;

  if (filtered.length === 0) {
    list.innerHTML = "<li>No configurations saved</li>";
    return;
  }

  list.innerHTML = filtered
    .map(
      (c) =>
        `<li>
          <span><span class="scope-badge scope-${c.scope}">${c.scope}</span> ${c.message.j_series} — ${c.name}</span>
          <span class="item-actions">
            <button data-link16-load-config="${encodeURIComponent(c.config_id)}">Load</button>
            <button data-link16-delete-config="${encodeURIComponent(c.config_id)}">Delete</button>
          </span>
        </li>`
    )
    .join("");

  list.querySelectorAll("[data-link16-load-config]").forEach((btn) => {
    btn.addEventListener("click", () =>
      loadLink16Configuration(decodeURIComponent(btn.dataset.link16LoadConfig))
    );
  });
  list.querySelectorAll("[data-link16-delete-config]").forEach((btn) => {
    btn.addEventListener("click", () =>
      deleteLink16Configuration(decodeURIComponent(btn.dataset.link16DeleteConfig))
    );
  });
}

async function loadLink16Configuration(configId) {
  const config = await api(`/configurations/${encodeURIComponent(configId)}`);
  await selectMessage(config.message.j_series);
  state.fieldValues = config.message.fields;
  renderForm();
  navigateTo("link16", "message");
}

async function deleteLink16Configuration(configId) {
  if (!confirm("Delete this configuration?")) return;
  await api(`/configurations/${encodeURIComponent(configId)}`, { method: "DELETE" });
  loadLink16Library();
}

// --- Scenario ---

function buildLink16ScenarioPayload() {
  const name =
    document.getElementById("link16-scenario-name")?.value ||
    `Link 16 scenario ${new Date().toISOString().slice(0, 16)}`;
  return {
    id: state.activeScenarioId || `link16-${Date.now().toString(36)}`,
    name,
    transport: {
      host: document.getElementById("link16-scenario-host")?.value || "host.docker.internal",
      port: parseInt(document.getElementById("link16-scenario-port")?.value || "8700", 10),
      protocol: document.getElementById("link16-scenario-protocol")?.value || "udp",
    },
    loop_count: parseInt(document.getElementById("link16-scenario-loops")?.value || "1", 10),
    interval_ms: parseInt(document.getElementById("link16-scenario-interval")?.value || "1000", 10),
    steps: state.scenarioSteps,
  };
}

function renderLink16ScenarioSteps() {
  const container = document.getElementById("link16-scenario-steps");
  const countEl = document.getElementById("link16-step-count");
  if (!container) return;

  if (countEl) {
    countEl.textContent =
      state.scenarioSteps.length === 1 ? "1 step" : `${state.scenarioSteps.length} steps`;
  }

  container.innerHTML = state.scenarioSteps.length
    ? state.scenarioSteps
        .map(
          (step, i) =>
            `<div class="scenario-step-card">
              <strong>Step ${i + 1}</strong> — ${step.name || step.message.j_series}
              <span class="muted">${step.message.j_series} · delay ${step.delay_ms}ms · repeat ${step.repeat}</span>
              <button type="button" data-link16-remove-step="${i}" class="btn secondary btn-sm">Remove</button>
            </div>`
        )
        .join("")
    : '<p class="muted">No steps yet.</p>';

  container.querySelectorAll("[data-link16-remove-step]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.scenarioSteps.splice(parseInt(btn.dataset.link16RemoveStep, 10), 1);
      updateLink16ScenarioUI();
    });
  });

  updateLink16ScenarioUI();
}

function updateLink16ScenarioUI() {
  const hasSteps = state.scenarioSteps.length > 0;
  const start = document.getElementById("btn-link16-start-scenario");
  const pause = document.getElementById("btn-link16-pause-scenario");
  const resume = document.getElementById("btn-link16-resume-scenario");
  const stop = document.getElementById("btn-link16-stop-scenario");
  if (start) start.disabled = !hasSteps || state.scenarioRunning;
  if (pause) pause.disabled = !state.scenarioRunning || state.scenarioPaused;
  if (resume) resume.disabled = !state.scenarioPaused;
  if (stop) stop.disabled = !state.scenarioRunning;
}

function addLink16StepFromCurrentMessage() {
  if (!state.selectedSeries) {
    alert("Select a J-message first.");
    return false;
  }
  state.scenarioSteps.push({
    id: `step-${Date.now().toString(36)}`,
    name: `${state.selectedSeries} step`,
    message: getCurrentMessage(),
    delay_ms: 0,
    repeat: 1,
  });
  renderLink16ScenarioSteps();
  return true;
}

document.getElementById("btn-link16-add-step")?.addEventListener("click", () => {
  if (addLink16StepFromCurrentMessage()) navigateTo("link16", "scenario");
});

document.getElementById("btn-link16-add-step-panel")?.addEventListener("click", addLink16StepFromCurrentMessage);

document.getElementById("btn-link16-start-scenario")?.addEventListener("click", async () => {
  try {
    const scenario = buildLink16ScenarioPayload();
    await api("/scenarios/validate", { method: "POST", body: JSON.stringify(scenario) });
    const runState = await api("/scenarios/run", { method: "POST", body: JSON.stringify(scenario) });
    state.activeScenarioId = runState.scenario_id;
    state.scenarioRunning = true;
    startLink16StatusPolling();
  } catch (err) {
    document.getElementById("link16-scenario-status").textContent = `Error: ${err.message}`;
  }
});

async function controlLink16Scenario(action) {
  if (!state.activeScenarioId) return;
  await api(`/scenarios/runs/${state.activeScenarioId}/${action}`, { method: "POST" });
  pollLink16ScenarioStatus();
}

document.getElementById("btn-link16-pause-scenario")?.addEventListener("click", () =>
  controlLink16Scenario("pause")
);
document.getElementById("btn-link16-resume-scenario")?.addEventListener("click", () =>
  controlLink16Scenario("resume")
);
document.getElementById("btn-link16-stop-scenario")?.addEventListener("click", () =>
  controlLink16Scenario("stop")
);

function startLink16StatusPolling() {
  if (state.statusPollTimer) clearInterval(state.statusPollTimer);
  pollLink16ScenarioStatus();
  state.statusPollTimer = setInterval(pollLink16ScenarioStatus, 500);
}

async function pollLink16ScenarioStatus() {
  if (!state.activeScenarioId) return;
  try {
    const runState = await api(`/scenarios/runs/${state.activeScenarioId}`);
    document.getElementById("link16-scenario-status").textContent =
      `Status: ${runState.status}\nStep: ${runState.current_step + 1} / ${state.scenarioSteps.length}\n` +
      `Messages sent: ${runState.messages_sent}` +
      (runState.error ? `\nError: ${runState.error}` : "");

    state.scenarioRunning = ["running", "paused"].includes(runState.status);
    state.scenarioPaused = runState.status === "paused";
    updateLink16ScenarioUI();

    if (["completed", "stopped", "error"].includes(runState.status)) {
      clearInterval(state.statusPollTimer);
      state.statusPollTimer = null;
      state.scenarioRunning = false;
      state.scenarioPaused = false;
      updateLink16ScenarioUI();
    }
  } catch {
    clearInterval(state.statusPollTimer);
    state.statusPollTimer = null;
    state.scenarioRunning = false;
    updateLink16ScenarioUI();
  }
}

document.getElementById("btn-link16-save-scenario")?.addEventListener("click", async () => {
  if (state.scenarioSteps.length === 0) {
    alert("Add at least one step.");
    return;
  }
  const scenario = buildLink16ScenarioPayload();
  await api("/saved-scenarios", { method: "POST", body: JSON.stringify(scenario) });
  state.activeScenarioId = scenario.id;
  alert(`Saved to data/link16_scenarios/${scenario.id}.json`);
});

async function loadLink16SavedScenario(id) {
  const scenario = await api(`/saved-scenarios/${id}`);
  state.scenarioSteps = scenario.steps;
  state.activeScenarioId = scenario.id;
  document.getElementById("link16-scenario-name").value = scenario.name;
  document.getElementById("link16-scenario-loops").value = scenario.loop_count;
  document.getElementById("link16-scenario-interval").value = scenario.interval_ms;
  document.getElementById("link16-scenario-host").value = scenario.transport.host;
  document.getElementById("link16-scenario-port").value = scenario.transport.port;
  document.getElementById("link16-scenario-protocol").value = scenario.transport.protocol;
  renderLink16ScenarioSteps();
  navigateTo("link16", "scenario");
}

async function deleteLink16SavedScenario(id) {
  if (!confirm("Delete this scenario?")) return;
  await api(`/saved-scenarios/${id}`, { method: "DELETE" });
  loadLink16Library();
}

onNavigate(({ protocol, subtab }) => {
  if (protocol !== "link16") return;
  if (subtab === "library") loadLink16Library();
  if (subtab === "scenario") updateLink16ScenarioUI();
});

renderLink16ScenarioSteps();
