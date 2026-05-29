/**
 * Obelix frontend – ASTERIX message editor and scenario builder.
 */

const API = "/api";

const state = {
  categories: [],
  selectedCategory: null,
  categoryDef: null,
  fieldValues: {},
  scenarioSteps: [],
  activeScenarioId: null,
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

  document.querySelectorAll("#category-list li").forEach((li) => {
    li.classList.toggle("active", parseInt(li.dataset.category, 10) === category);
  });

  document.getElementById("category-title").textContent =
    `Category ${category} – ${state.categoryDef.name}`;
  document.getElementById("category-description").textContent = state.categoryDef.description;

  renderForm();
  document.getElementById("hex-output").textContent = "—";
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

// --- Templates ---

document.getElementById("btn-save-template").addEventListener("click", async () => {
  const name = prompt("Template name:");
  if (!name) return;
  const id = name.toLowerCase().replace(/\s+/g, "-") + "-" + Date.now().toString(36);

  try {
    await api("/templates", {
      method: "POST",
      body: JSON.stringify({
        id,
        name,
        message: getCurrentMessage(),
      }),
    });
    alert(`Template "${name}" saved.`);
  } catch (err) {
    alert(`Failed to save: ${err.message}`);
  }
});

async function loadLibrary() {
  const templates = await api("/templates");
  const scenarios = await api("/saved-scenarios");

  document.getElementById("template-list").innerHTML = templates.length
    ? templates
        .map(
          (t) =>
            `<li>
              <span>${t.name} (Cat ${t.message.category})</span>
              <span class="item-actions">
                <button data-load-template="${t.id}">Load</button>
                <button data-delete-template="${t.id}">Delete</button>
              </span>
            </li>`
        )
        .join("")
    : "<li>No templates saved</li>";

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

  document.querySelectorAll("[data-load-template]").forEach((btn) => {
    btn.addEventListener("click", () => loadTemplate(btn.dataset.loadTemplate));
  });
  document.querySelectorAll("[data-delete-template]").forEach((btn) => {
    btn.addEventListener("click", () => deleteTemplate(btn.dataset.deleteTemplate));
  });
  document.querySelectorAll("[data-load-scenario]").forEach((btn) => {
    btn.addEventListener("click", () => loadSavedScenario(btn.dataset.loadScenario));
  });
  document.querySelectorAll("[data-delete-scenario]").forEach((btn) => {
    btn.addEventListener("click", () => deleteSavedScenario(btn.dataset.deleteScenario));
  });
}

async function loadTemplate(id) {
  const template = await api(`/templates/${id}`);
  await selectCategory(template.message.category);
  state.fieldValues = template.message.fields;
  renderForm();
  document.querySelector('[data-tab="message"]').click();
}

async function deleteTemplate(id) {
  if (!confirm("Delete this template?")) return;
  await api(`/templates/${id}`, { method: "DELETE" });
  loadLibrary();
}

// --- Scenario Builder ---

function renderScenarioSteps() {
  const container = document.getElementById("scenario-steps");
  if (state.scenarioSteps.length === 0) {
    container.innerHTML = "<p class='muted'>No steps yet. Add a step from the current message.</p>";
    return;
  }

  container.innerHTML = state.scenarioSteps
    .map(
      (step, i) =>
        `<div class="step-item" data-step="${i}">
          <span><strong>Step ${i + 1}</strong>: Cat ${step.message.category} – ${step.name || "Unnamed"}</span>
          <label>Delay (ms) <input type="number" data-step-delay="${i}" value="${step.delay_ms}" min="0"></label>
          <label>Repeat <input type="number" data-step-repeat="${i}" value="${step.repeat}" min="1"></label>
          <button type="button" data-remove-step="${i}" class="btn danger">Remove</button>
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
  container.querySelectorAll("[data-remove-step]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.scenarioSteps.splice(parseInt(btn.dataset.removeStep, 10), 1);
      renderScenarioSteps();
    });
  });
}

document.getElementById("btn-add-step").addEventListener("click", () => {
  if (!state.selectedCategory) {
    alert("Select a category and configure a message first.");
    return;
  }
  const name = `Cat ${state.selectedCategory} message`;
  state.scenarioSteps.push({
    id: "step-" + Date.now().toString(36),
    name,
    message: getCurrentMessage(),
    delay_ms: state.scenarioSteps.length === 0 ? 0 : 500,
    repeat: 1,
  });
  renderScenarioSteps();
});

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
    alert("Add at least one step to the scenario.");
    return;
  }
  try {
    const scenario = buildScenarioPayload();
    const runState = await api("/scenarios/run", {
      method: "POST",
      body: JSON.stringify(scenario),
    });
    state.activeScenarioId = runState.scenario_id;
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
    document.getElementById("scenario-status").textContent =
      `Status: ${runState.status}\n` +
      `Step: ${runState.current_step + 1} / ${state.scenarioSteps.length}\n` +
      `Loop: ${runState.current_loop + 1}\n` +
      `Messages sent: ${runState.messages_sent}` +
      (runState.error ? `\nError: ${runState.error}` : "");

    if (["completed", "stopped", "error"].includes(runState.status)) {
      clearInterval(state.statusPollTimer);
      state.statusPollTimer = null;
    }
  } catch {
    clearInterval(state.statusPollTimer);
    state.statusPollTimer = null;
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
  state.scenarioSteps = scenario.steps;
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
