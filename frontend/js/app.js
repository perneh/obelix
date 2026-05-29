/**
 * Obelix frontend – ASTERIX message editor and scenario builder.
 */

import { renderMarkdown } from "./markdown.js";
import {
  ensureStepMotion,
  formatWaypointSummary,
  motionFieldConfig,
  motionMessageCount,
  stepDistanceHint,
  stepDistanceLabel,
  supportsMotion,
} from "./motion.js";

const API = "/api";

const state = {
  categories: [],
  selectedCategory: null,
  categoryDef: null,
  categoryHelp: null,
  helpPanelOpen: false,
  fieldValues: {},
  scenarioSteps: [],
  activeScenarioId: null,
  scenarioRunning: false,
  scenarioPaused: false,
  statusPollTimer: null,
};

// --- API helpers ---

async function api(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  if (res.status === 204) return null;
  return res.json();
}

// --- Tabs ---

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(`tab-${tab.dataset.tab}`).classList.add("active");
    if (tab.dataset.tab === "library") loadLibrary();
    if (tab.dataset.tab === "scenario") updateScenarioUI();
  });
});

// --- Categories ---

async function loadCategories() {
  state.categories = await api("/categories");
  const list = document.getElementById("category-list");
  list.innerHTML = state.categories
    .map(
      (cat) =>
        `<li data-category="${cat.category}">
          <span class="cat-num">Cat ${cat.category}</span>${cat.name}
        </li>`
    )
    .join("");

  list.querySelectorAll("li").forEach((li) => {
    li.addEventListener("click", () => selectCategory(parseInt(li.dataset.category, 10)));
  });

  if (state.categories.length > 0) {
    selectCategory(state.categories[0].category);
  }
}

async function selectCategory(category) {
  state.selectedCategory = category;
  state.categoryDef = await api(`/categories/${category}`);
  state.fieldValues = buildDefaults(state.categoryDef.fields);
  state.categoryHelp = null;
  state.helpPanelOpen = false;

  document.querySelectorAll("#category-list li").forEach((li) => {
    li.classList.toggle("active", parseInt(li.dataset.category, 10) === category);
  });

  document.getElementById("category-title").textContent =
    `Category ${category} – ${state.categoryDef.name}`;
  document.getElementById("category-description").textContent = state.categoryDef.description;

  const helpBtn = document.getElementById("btn-category-help");
  helpBtn.hidden = false;
  helpBtn.setAttribute("aria-expanded", "false");
  hideCategoryHelp();

  renderForm();
  document.getElementById("hex-output").textContent = "—";
}

async function loadCategoryHelp() {
  if (state.categoryHelp) return state.categoryHelp;
  state.categoryHelp = await api(`/categories/${state.selectedCategory}/help`);
  return state.categoryHelp;
}

function hideCategoryHelp() {
  const panel = document.getElementById("category-help-panel");
  panel.classList.add("hidden");
  panel.innerHTML = "";
  state.helpPanelOpen = false;
  document.getElementById("btn-category-help").setAttribute("aria-expanded", "false");
}

async function toggleCategoryHelp() {
  const panel = document.getElementById("category-help-panel");
  const helpBtn = document.getElementById("btn-category-help");

  if (state.helpPanelOpen) {
    hideCategoryHelp();
    return;
  }

  try {
    helpBtn.disabled = true;
    const help = await loadCategoryHelp();
    panel.innerHTML = `<article class="help-content">${renderMarkdown(help.content)}</article>`;
    panel.classList.remove("hidden");
    state.helpPanelOpen = true;
    helpBtn.setAttribute("aria-expanded", "true");
  } catch (err) {
    panel.innerHTML = `<p class="status error">Could not load help: ${err.message}</p>`;
    panel.classList.remove("hidden");
  } finally {
    helpBtn.disabled = false;
  }
}

document.getElementById("btn-category-help").addEventListener("click", toggleCategoryHelp);

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

function renderForm() {
  const form = document.getElementById("message-form");
  form.innerHTML = state.categoryDef.fields.map((field) => renderField(field)).join("");

  form.querySelectorAll("[data-field]").forEach((el) => {
    el.addEventListener("change", onFieldChange);
    el.addEventListener("input", onFieldChange);
  });
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
        <label for="field-${fieldKey}">${field.label}</label>
        ${field.description ? `<div class="field-desc">${field.description}</div>` : ""}
        <select id="field-${fieldKey}" data-field="${fieldKey}">
          ${field.options
            .map(
              (opt) =>
                `<option value="${opt.value}" ${opt.value === value ? "selected" : ""}>${opt.label}</option>`
            )
            .join("")}
        </select>
      </div>`;
  }

  const inputType = field.type === "float" ? "number" : "number";
  const step = field.type === "float" ? "any" : "1";
  const min = field.min !== undefined ? `min="${field.min}"` : "";
  const max = field.max !== undefined ? `max="${field.max}"` : "";
  const unit = field.unit ? ` (${field.unit})` : "";

  return `
    <div class="field-group">
      <label for="field-${fieldKey}">${field.label}${unit}</label>
      ${field.description ? `<div class="field-desc">${field.description}</div>` : ""}
      <input type="${inputType}" id="field-${fieldKey}" data-field="${fieldKey}"
        value="${value}" step="${step}" ${min} ${max}>
    </div>`;
}

function onFieldChange(e) {
  const key = e.target.dataset.field;
  const parts = key.split(".");
  if (parts.length === 2) {
    if (!state.fieldValues[parts[0]]) state.fieldValues[parts[0]] = {};
    const fieldDef = findFieldDef(parts[0], parts[1]);
    state.fieldValues[parts[0]][parts[1]] = parseFieldValue(e.target.value, fieldDef);
  } else {
    const fieldDef = state.categoryDef.fields.find((f) => f.id === key);
    state.fieldValues[key] = parseFieldValue(e.target.value, fieldDef);
  }

  if (key === "message_type" || parts.includes("message_type")) {
    renderForm();
  }
}

function findFieldDef(parentId, subId) {
  const parent = state.categoryDef.fields.find((f) => f.id === parentId);
  return parent?.fields?.find((f) => f.id === subId);
}

function parseFieldValue(raw, fieldDef) {
  if (!fieldDef) return raw;
  if (fieldDef.type === "float") return parseFloat(raw);
  if (fieldDef.type === "enum") return parseInt(raw, 10);
  return parseInt(raw, 10);
}

function getCurrentMessage() {
  return {
    category: state.selectedCategory,
    fields: structuredClone(state.fieldValues),
  };
}

// --- Encode & Send ---

document.getElementById("btn-encode").addEventListener("click", async () => {
  try {
    const result = await api("/encode", {
      method: "POST",
      body: JSON.stringify({ message: getCurrentMessage() }),
    });
    document.getElementById("hex-output").textContent =
      `${result.hex}\n(${result.length} bytes, Category ${result.category})`;
  } catch (err) {
    document.getElementById("hex-output").textContent = `Error: ${err.message}`;
  }
});

document.getElementById("btn-send").addEventListener("click", async () => {
  const statusEl = document.getElementById("send-status");
  statusEl.textContent = "Sending…";
  statusEl.className = "status";

  try {
    const result = await api("/send", {
      method: "POST",
      body: JSON.stringify({
        message: getCurrentMessage(),
        host: document.getElementById("send-host").value,
        port: parseInt(document.getElementById("send-port").value, 10),
        protocol: document.getElementById("send-protocol").value,
      }),
    });
    statusEl.textContent = `Sent ${result.bytes_sent} bytes to ${result.host}:${result.port} via ${result.protocol.toUpperCase()}`;
    statusEl.className = "status success";

    const enc = await api("/encode", {
      method: "POST",
      body: JSON.stringify({ message: getCurrentMessage() }),
    });
    document.getElementById("hex-output").textContent =
      `${enc.hex}\n(${enc.length} bytes)`;
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
    statusEl.className = "status error";
  }
});

// --- Configurations ---

function slugify(name) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

async function saveConfiguration(scope) {
  const name = prompt("Configuration name:");
  if (!name) return;

  const description = prompt("Description (optional):") || "";
  const id = slugify(name);
  if (!id) {
    alert("Invalid name.");
    return;
  }

  try {
    await api("/configurations", {
      method: "POST",
      body: JSON.stringify({
        id,
        name,
        description,
        scope,
        message: getCurrentMessage(),
      }),
    });
    const where = scope === "shared" ? "configurations/" : "data/configurations/";
    alert(`Saved "${name}" to ${where}cat${String(state.selectedCategory).padStart(3, "0")}/`);
  } catch (err) {
    alert(`Failed to save: ${err.message}`);
  }
}

document.getElementById("btn-save-local").addEventListener("click", () => saveConfiguration("local"));
document.getElementById("btn-save-shared").addEventListener("click", () => saveConfiguration("shared"));

function renderConfigurationList(configurations) {
  const filter = document.getElementById("config-category-filter").value;
  const filtered = filter
    ? configurations.filter((c) => String(c.message.category) === filter)
    : configurations;

  const grouped = filtered.reduce((acc, config) => {
    const cat = config.message.category;
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(config);
    return acc;
  }, {});

  const categories = Object.keys(grouped).sort((a, b) => Number(a) - Number(b));

  if (categories.length === 0) {
    document.getElementById("configuration-list").innerHTML = "<li>No configurations saved</li>";
    return;
  }

  document.getElementById("configuration-list").innerHTML = categories
    .map((cat) => {
      const items = grouped[cat]
        .map(
          (c) =>
            `<li>
              <span>
                <span class="scope-badge scope-${c.scope}">${c.scope}</span>
                ${c.name}
                <span class="muted">(${c.id})</span>
              </span>
              <span class="item-actions">
                <button data-load-config="${encodeURIComponent(c.config_id)}">Load</button>
                <button data-delete-config="${encodeURIComponent(c.config_id)}">Delete</button>
              </span>
            </li>`
        )
        .join("");
      return `<li class="config-group-header"><strong>Category ${cat}</strong></li>${items}`;
    })
    .join("");

  document.querySelectorAll("[data-load-config]").forEach((btn) => {
    btn.addEventListener("click", () => loadConfiguration(decodeURIComponent(btn.dataset.loadConfig)));
  });
  document.querySelectorAll("[data-delete-config]").forEach((btn) => {
    btn.addEventListener("click", () => deleteConfiguration(decodeURIComponent(btn.dataset.deleteConfig)));
  });
}

async function loadLibrary() {
  const configurations = await api("/configurations");
  const scenarios = await api("/saved-scenarios");

  configurations.forEach((c) => {
    c.config_id = c.config_id || `${c.scope}:cat${String(c.message.category).padStart(3, "0")}:${c.id}`;
  });

  const filterSelect = document.getElementById("config-category-filter");
  const currentFilter = filterSelect.value;
  const categoryIds = [...new Set(configurations.map((c) => c.message.category))].sort((a, b) => a - b);
  filterSelect.innerHTML =
    `<option value="">All categories</option>` +
    categoryIds.map((cat) => `<option value="${cat}">Category ${cat}</option>`).join("");
  filterSelect.value = currentFilter;
  filterSelect.onchange = () => renderConfigurationList(configurations);

  renderConfigurationList(configurations);

  document.getElementById("saved-scenario-list").innerHTML = scenarios.length
    ? scenarios
        .map(
          (s) =>
            `<li>
              <span>${s.name} (${s.steps.length} steps)</span>
              <span class="item-actions">
                <button data-load-scenario="${s.id}">Load</button>
                <button data-delete-scenario="${s.id}">Delete</button>
              </span>
            </li>`
        )
        .join("")
    : "<li>No scenarios saved</li>";

  document.querySelectorAll("[data-load-scenario]").forEach((btn) => {
    btn.addEventListener("click", () => loadSavedScenario(btn.dataset.loadScenario));
  });
  document.querySelectorAll("[data-delete-scenario]").forEach((btn) => {
    btn.addEventListener("click", () => deleteSavedScenario(btn.dataset.deleteScenario));
  });
}

async function loadConfiguration(configId) {
  const config = await api(`/configurations/${configId}`);
  await selectCategory(config.message.category);
  state.fieldValues = config.message.fields;
  renderForm();
  document.querySelector('[data-tab="message"]').click();
}

async function deleteConfiguration(configId) {
  if (!confirm("Delete this configuration?")) return;
  await api(`/configurations/${configId}`, { method: "DELETE" });
  loadLibrary();
}

// --- Scenario Builder ---

function updateScenarioUI() {
  const count = state.scenarioSteps.length;
  const countEl = document.getElementById("scenario-step-count");
  if (countEl) {
    countEl.textContent = count === 1 ? "1 step" : `${count} steps`;
  }

  const startBtn = document.getElementById("btn-start-scenario");
  const canStart = count > 0 && !state.scenarioRunning;
  if (startBtn) {
    startBtn.disabled = !canStart;
    startBtn.title = count === 0 ? "Add at least one step first" : "";
  }

  const isRunning = state.scenarioRunning;
  const isPaused = state.scenarioPaused;
  const pauseBtn = document.getElementById("btn-pause-scenario");
  const resumeBtn = document.getElementById("btn-resume-scenario");
  const stopBtn = document.getElementById("btn-stop-scenario");
  if (pauseBtn) pauseBtn.disabled = !isRunning || isPaused;
  if (resumeBtn) resumeBtn.disabled = !isPaused;
  if (stopBtn) stopBtn.disabled = !isRunning && !isPaused;

  document.querySelectorAll(".workflow-step").forEach((el) => {
    el.classList.remove("active", "done");
  });
  const wfCreate = document.querySelector('[data-wf="create"]');
  const wfAdd = document.querySelector('[data-wf="add"]');
  const wfConfigure = document.querySelector('[data-wf="configure"]');
  const wfRun = document.querySelector('[data-wf="run"]');

  if (count === 0) {
    wfCreate?.classList.add("active");
  } else {
    wfCreate?.classList.add("done");
    wfAdd?.classList.add("done");
    if (isRunning || isPaused) {
      wfConfigure?.classList.add("done");
      wfRun?.classList.add("active");
    } else {
      wfConfigure?.classList.add("active");
    }
  }
}

async function addStepFromCurrentMessage() {
  if (!state.selectedCategory) {
    alert("Select a category in Message Editor first, then configure the message fields.");
    document.querySelector('[data-tab="message"]')?.click();
    return false;
  }
  const message = getCurrentMessage();
  const name = `Cat ${state.selectedCategory} message`;
  let motion = null;
  if (supportsMotion(message.category)) {
    try {
      motion = await api("/scenarios/motion-defaults", {
        method: "POST",
        body: JSON.stringify({ message }),
      });
    } catch {
      const step = { message };
      ensureStepMotion(step);
      motion = step.motion;
    }
  }
  state.scenarioSteps.push({
    id: "step-" + Date.now().toString(36),
    name,
    message,
    delay_ms: state.scenarioSteps.length === 0 ? 0 : 500,
    repeat: 1,
    motion,
  });
  renderScenarioSteps();
  return true;
}

document.getElementById("btn-goto-message")?.addEventListener("click", () => {
  document.querySelector('[data-tab="message"]')?.click();
});

document.getElementById("btn-add-to-scenario")?.addEventListener("click", async () => {
  const added = await addStepFromCurrentMessage();
  if (added) {
    document.querySelector('[data-tab="scenario"]')?.click();
  }
});

function renderMotionSection(step, index) {
  const cat = step.message.category;
  if (!supportsMotion(cat)) {
    return `<p class="muted motion-unsupported">Route animation is not available for category ${cat}. Use <strong>Repeat</strong> to send the same message multiple times.</p>`;
  }

  ensureStepMotion(step);
  const motion = step.motion;
  const mode = motion.mode || "direction";
  const endWp = motion.waypoints[1] || {};
  const fields = step.message.fields;
  const fieldCfg = motionFieldConfig(cat, fields);
  const startSummary = formatWaypointSummary(cat, fields, motion.waypoints[0]);
  const msgCount = motionMessageCount(step);

  const endFields = fieldCfg
    .map(
      ({ key, label, unit }) =>
        `<label>${label}${unit ? ` (${unit})` : ""}
          <input type="number" step="any" data-motion-end="${index}.${key}"
            value="${endWp[key] ?? ""}">
        </label>`
    )
    .join("");

  return `
    <div class="motion-section">
      <label class="motion-toggle">
        <input type="checkbox" data-motion-enabled="${index}" ${motion.enabled ? "checked" : ""}>
        Send multiple messages — move position over time
      </label>
      <div class="motion-details ${motion.enabled ? "" : "hidden"}">
        <p class="motion-summary"><strong>${msgCount} messages</strong> will be sent from the start position.</p>
        <fieldset class="motion-mode-fieldset">
          <legend>How should position change?</legend>
          <label class="motion-mode-option">
            <input type="radio" name="motion-mode-${index}" value="direction" data-motion-mode="${index}"
              ${mode === "direction" ? "checked" : ""}>
            <span><strong>Direction from start</strong> — pick heading and distance per message (only start point needed)</span>
          </label>
          <label class="motion-mode-option">
            <input type="radio" name="motion-mode-${index}" value="waypoints" data-motion-mode="${index}"
              ${mode === "waypoints" ? "checked" : ""}>
            <span><strong>Route to endpoint</strong> — interpolate between start and end coordinates</span>
          </label>
        </fieldset>
        <p class="muted">Start: ${startSummary || "from message fields"}</p>
        <div class="motion-direction-fields ${mode === "direction" ? "" : "hidden"}">
          <div class="form-row">
            <label>Heading (°)
              <input type="number" step="any" data-motion-heading="${index}" value="${motion.heading_deg ?? 90}" min="0" max="360">
              <span class="field-hint">0 = North, 90 = East, 180 = South, 270 = West</span>
            </label>
            <label>${stepDistanceLabel(cat)}
              <input type="number" step="any" data-motion-distance="${index}" value="${motion.step_distance ?? 1000}" min="0.001">
              <span class="field-hint">${stepDistanceHint(cat)}</span>
            </label>
          </div>
        </div>
        <div class="motion-waypoint-fields ${mode === "waypoints" ? "" : "hidden"}">
          <p class="field-hint">Set the end position — Obelix interpolates between start and end.</p>
          <div class="form-row motion-end-fields">${endFields}</div>
        </div>
        <div class="form-row">
          <label>Number of messages
            <input type="number" data-motion-ticks="${index}" value="${motion.ticks}" min="2">
            <span class="field-hint">How many updates to send for this step</span>
          </label>
          <label>Interval (ms)
            <input type="number" data-motion-interval="${index}" value="${motion.tick_interval_ms}" min="0">
            <span class="field-hint">Wait time between each message</span>
          </label>
        </div>
        <div class="form-row motion-options">
          <label class="motion-toggle">
            <input type="checkbox" data-motion-time="${index}" ${motion.update_time ? "checked" : ""}>
            Advance time of track
          </label>
          ${
            cat === 62
              ? `<label class="motion-toggle">
                  <input type="checkbox" data-motion-velocity="${index}" ${motion.derive_velocity ? "checked" : ""}>
                  Derive velocity from movement
                </label>`
              : ""
          }
        </div>
      </div>
    </div>`;
}

function renderScenarioSteps() {
  const container = document.getElementById("scenario-steps");
  if (state.scenarioSteps.length === 0) {
    container.innerHTML = `
      <div class="steps-empty">
        <p><strong>No steps yet.</strong> A scenario needs at least one message to send.</p>
        <ol>
          <li>Open <button type="button" class="link-btn" data-goto-message>Message Editor</button> and configure a message</li>
          <li>Return here and click <strong>+ Add Step from Current Message</strong></li>
          <li>Enable <strong>Send multiple messages</strong> — set heading, distance, count and interval</li>
          <li>Add more steps with <strong>+ Add Step</strong>, or edit with <strong>Update from Editor</strong></li>
        </ol>
      </div>`;
    container.querySelector("[data-goto-message]")?.addEventListener("click", () => {
      document.querySelector('[data-tab="message"]')?.click();
    });
    updateScenarioUI();
    return;
  }

  container.innerHTML = state.scenarioSteps
    .map(
      (step, i) =>
        `<div class="step-card" data-step="${i}">
          <div class="step-header">
            <span>
              <strong>Step ${i + 1}</strong>: Cat ${step.message.category} – ${step.name || "Unnamed"}
              <span class="step-msg-badge">${motionMessageCount(step)} msg</span>
            </span>
            <div class="step-header-actions">
              <button type="button" data-update-step="${i}" class="btn secondary btn-sm" title="Replace this step with the current Message Editor settings">Update from Editor</button>
              <button type="button" data-remove-step="${i}" class="btn danger btn-sm">Remove</button>
            </div>
          </div>
          <div class="form-row">
            <label>Wait before this step (ms)
              <input type="number" data-step-delay="${i}" value="${step.delay_ms}" min="0">
              <span class="field-hint">${i === 0 ? "Usually 0 for the first step" : "Pause after previous step finishes"}</span>
            </label>
            <label>Repeat (same message, no movement)
              <input type="number" data-step-repeat="${i}" value="${step.repeat}" min="1"
                ${step.motion?.enabled ? "disabled title='Use motion settings below instead'" : ""}>
              <span class="field-hint">Send identical message N times — or enable motion below to move</span>
            </label>
          </div>
          ${renderMotionSection(step, i)}
        </div>`
    )
    .join("");

  container.querySelectorAll("[data-step-delay]").forEach((el) => {
    el.addEventListener("change", () => {
      state.scenarioSteps[parseInt(el.dataset.stepDelay, 10)].delay_ms = parseInt(el.value, 10);
    });
  });
  container.querySelectorAll("[data-step-repeat]").forEach((el) => {
    el.addEventListener("change", () => {
      state.scenarioSteps[parseInt(el.dataset.stepRepeat, 10)].repeat = parseInt(el.value, 10);
    });
  });
  container.querySelectorAll("[data-motion-enabled]").forEach((el) => {
    el.addEventListener("change", () => {
      const idx = parseInt(el.dataset.motionEnabled, 10);
      ensureStepMotion(state.scenarioSteps[idx]);
      state.scenarioSteps[idx].motion.enabled = el.checked;
      renderScenarioSteps();
    });
  });
  container.querySelectorAll("[data-motion-mode]").forEach((el) => {
    el.addEventListener("change", () => {
      if (!el.checked) return;
      const idx = parseInt(el.dataset.motionMode, 10);
      ensureStepMotion(state.scenarioSteps[idx]);
      state.scenarioSteps[idx].motion.mode = el.value;
      renderScenarioSteps();
    });
  });
  container.querySelectorAll("[data-motion-heading]").forEach((el) => {
    el.addEventListener("change", () => {
      const idx = parseInt(el.dataset.motionHeading, 10);
      ensureStepMotion(state.scenarioSteps[idx]);
      state.scenarioSteps[idx].motion.heading_deg = parseFloat(el.value);
    });
  });
  container.querySelectorAll("[data-motion-distance]").forEach((el) => {
    el.addEventListener("change", () => {
      const idx = parseInt(el.dataset.motionDistance, 10);
      ensureStepMotion(state.scenarioSteps[idx]);
      state.scenarioSteps[idx].motion.step_distance = parseFloat(el.value);
    });
  });
  container.querySelectorAll("[data-motion-ticks]").forEach((el) => {
    el.addEventListener("change", () => {
      const idx = parseInt(el.dataset.motionTicks, 10);
      ensureStepMotion(state.scenarioSteps[idx]);
      state.scenarioSteps[idx].motion.ticks = Math.max(2, parseInt(el.value, 10));
    });
  });
  container.querySelectorAll("[data-motion-interval]").forEach((el) => {
    el.addEventListener("change", () => {
      const idx = parseInt(el.dataset.motionInterval, 10);
      ensureStepMotion(state.scenarioSteps[idx]);
      state.scenarioSteps[idx].motion.tick_interval_ms = parseInt(el.value, 10);
    });
  });
  container.querySelectorAll("[data-motion-time]").forEach((el) => {
    el.addEventListener("change", () => {
      const idx = parseInt(el.dataset.motionTime, 10);
      ensureStepMotion(state.scenarioSteps[idx]);
      state.scenarioSteps[idx].motion.update_time = el.checked;
    });
  });
  container.querySelectorAll("[data-motion-velocity]").forEach((el) => {
    el.addEventListener("change", () => {
      const idx = parseInt(el.dataset.motionVelocity, 10);
      ensureStepMotion(state.scenarioSteps[idx]);
      state.scenarioSteps[idx].motion.derive_velocity = el.checked;
    });
  });
  container.querySelectorAll("[data-motion-end]").forEach((el) => {
    el.addEventListener("change", () => {
      const [idxStr, key] = el.dataset.motionEnd.split(".");
      const idx = parseInt(idxStr, 10);
      ensureStepMotion(state.scenarioSteps[idx]);
      if (!state.scenarioSteps[idx].motion.waypoints[1]) {
        state.scenarioSteps[idx].motion.waypoints[1] = {};
      }
      state.scenarioSteps[idx].motion.waypoints[1][key] = parseFloat(el.value);
    });
  });
  container.querySelectorAll("[data-remove-step]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.scenarioSteps.splice(parseInt(btn.dataset.removeStep, 10), 1);
      renderScenarioSteps();
    });
  });
  container.querySelectorAll("[data-update-step]").forEach((btn) => {
    btn.addEventListener("click", () => updateStepFromEditor(parseInt(btn.dataset.updateStep, 10)));
  });
  updateScenarioUI();
}

async function updateStepFromEditor(index) {
  if (!state.selectedCategory) {
    alert("Open Message Editor and select a category first.");
    document.querySelector('[data-tab="message"]')?.click();
    return;
  }
  const step = state.scenarioSteps[index];
  const message = getCurrentMessage();
  if (message.category !== step.message.category) {
    const ok = confirm(
      `Message Editor has Cat ${message.category}, but this step is Cat ${step.message.category}.\nReplace step anyway?`
    );
    if (!ok) return;
  }
  step.message = message;
  step.name = `Cat ${message.category} message`;
  if (supportsMotion(message.category)) {
    try {
      const defaults = await api("/scenarios/motion-defaults", {
        method: "POST",
        body: JSON.stringify({ message }),
      });
      const prev = step.motion || {};
      step.motion = {
        ...defaults,
        enabled: prev.enabled ?? false,
        mode: prev.mode ?? defaults.mode,
        heading_deg: prev.heading_deg ?? defaults.heading_deg,
        step_distance: prev.step_distance ?? defaults.step_distance,
        ticks: prev.ticks ?? defaults.ticks,
        tick_interval_ms: prev.tick_interval_ms ?? defaults.tick_interval_ms,
        update_time: prev.update_time ?? defaults.update_time,
        derive_velocity: prev.derive_velocity ?? defaults.derive_velocity,
        waypoints: [defaults.waypoints[0], prev.waypoints?.[1] ?? defaults.waypoints[1]],
      };
    } catch {
      ensureStepMotion(step);
      step.motion.waypoints[0] = ensureStepMotion(step).waypoints[0];
    }
  }
  renderScenarioSteps();
}

document.getElementById("btn-add-step").addEventListener("click", () => addStepFromCurrentMessage());

function buildScenarioPayload() {
  const name = document.getElementById("scenario-name").value || "Unnamed scenario";
  const id = state.activeScenarioId || "scenario-" + Date.now().toString(36);
  return {
    id,
    name,
    transport: {
      host: document.getElementById("scenario-host").value,
      port: parseInt(document.getElementById("scenario-port").value, 10),
      protocol: document.getElementById("scenario-protocol").value,
    },
    loop_count: parseInt(document.getElementById("scenario-loops").value, 10),
    interval_ms: parseInt(document.getElementById("scenario-interval").value, 10),
    steps: state.scenarioSteps,
  };
}

document.getElementById("btn-start-scenario").addEventListener("click", async () => {
  if (state.scenarioSteps.length === 0) {
    alert("Add at least one step before starting.\n\n1. Open Message Editor\n2. Configure a message\n3. Click \"+ Add Step from Current Message\"");
    return;
  }
  try {
    const scenario = buildScenarioPayload();
    const runState = await api("/scenarios/run", {
      method: "POST",
      body: JSON.stringify(scenario),
    });
    state.activeScenarioId = runState.scenario_id;
    state.scenarioRunning = true;
    state.scenarioPaused = false;
    updateScenarioUI();
    document.getElementById("scenario-status").textContent = "Starting…";
    startStatusPolling();
  } catch (err) {
    document.getElementById("scenario-status").textContent = `Error: ${err.message}`;
  }
});

document.getElementById("btn-pause-scenario").addEventListener("click", () =>
  controlScenario("pause")
);
document.getElementById("btn-resume-scenario").addEventListener("click", () =>
  controlScenario("resume")
);
document.getElementById("btn-stop-scenario").addEventListener("click", () =>
  controlScenario("stop")
);

async function controlScenario(action) {
  if (!state.activeScenarioId) {
    alert("No active scenario.");
    return;
  }
  try {
    await api(`/scenarios/runs/${state.activeScenarioId}/${action}`, { method: "POST" });
    pollScenarioStatus();
  } catch (err) {
    document.getElementById("scenario-status").textContent = `Error: ${err.message}`;
  }
}

function startStatusPolling() {
  if (state.statusPollTimer) clearInterval(state.statusPollTimer);
  pollScenarioStatus();
  state.statusPollTimer = setInterval(pollScenarioStatus, 500);
}

async function pollScenarioStatus() {
  if (!state.activeScenarioId) return;
  try {
    const runState = await api(`/scenarios/runs/${state.activeScenarioId}`);
    const statusLabels = {
      running: "Running",
      paused: "Paused",
      completed: "Completed",
      stopped: "Stopped",
      error: "Error",
    };
    document.getElementById("scenario-status").textContent =
      `Status: ${statusLabels[runState.status] || runState.status}\n` +
      `Step: ${runState.current_step + 1} / ${state.scenarioSteps.length}\n` +
      `Loop: ${runState.current_loop + 1}\n` +
      `Messages sent: ${runState.messages_sent}` +
      (runState.error ? `\nError: ${runState.error}` : "");

    state.scenarioRunning = ["running", "paused"].includes(runState.status);
    state.scenarioPaused = runState.status === "paused";
    updateScenarioUI();

    if (["completed", "stopped", "error"].includes(runState.status)) {
      clearInterval(state.statusPollTimer);
      state.statusPollTimer = null;
      state.scenarioRunning = false;
      state.scenarioPaused = false;
      updateScenarioUI();
    }
  } catch {
    clearInterval(state.statusPollTimer);
    state.statusPollTimer = null;
    state.scenarioRunning = false;
    state.scenarioPaused = false;
    updateScenarioUI();
  }
}

document.getElementById("btn-save-scenario").addEventListener("click", async () => {
  if (state.scenarioSteps.length === 0) {
    alert("Add at least one step.");
    return;
  }
  try {
    const scenario = buildScenarioPayload();
    await api("/saved-scenarios", {
      method: "POST",
      body: JSON.stringify(scenario),
    });
    alert(`Scenario "${scenario.name}" saved.`);
  } catch (err) {
    alert(`Failed: ${err.message}`);
  }
});

async function loadSavedScenario(id) {
  const scenario = await api(`/saved-scenarios/${id}`);
  state.scenarioSteps = scenario.steps.map((step) => {
    if (step.motion) {
      ensureStepMotion(step);
    }
    return step;
  });
  state.activeScenarioId = scenario.id;
  document.getElementById("scenario-name").value = scenario.name;
  document.getElementById("scenario-loops").value = scenario.loop_count;
  document.getElementById("scenario-interval").value = scenario.interval_ms;
  document.getElementById("scenario-host").value = scenario.transport.host;
  document.getElementById("scenario-port").value = scenario.transport.port;
  document.getElementById("scenario-protocol").value = scenario.transport.protocol;
  renderScenarioSteps();
  document.querySelector('[data-tab="scenario"]').click();
}

async function deleteSavedScenario(id) {
  if (!confirm("Delete this scenario?")) return;
  await api(`/saved-scenarios/${id}`, { method: "DELETE" });
  loadLibrary();
}

// --- Init ---

loadCategories();
renderScenarioSteps();
updateScenarioUI();
