/** Export / import scenario JSON for external editing. */

export function scenarioToJsonString(scenario, pretty = true) {
  return pretty ? JSON.stringify(scenario, null, 2) : JSON.stringify(scenario);
}

export function parseScenarioJsonText(text) {
  const trimmed = text.trim();
  if (!trimmed) {
    throw new Error("JSON is empty.");
  }
  try {
    return JSON.parse(trimmed);
  } catch (err) {
    throw new Error(`Invalid JSON: ${err.message}`);
  }
}

export function scenarioFilename(scenario) {
  const base = (scenario.id || scenario.name || "scenario")
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, "-")
    .replace(/^-|-$/g, "");
  return `${base || "scenario"}.json`;
}

export function downloadScenarioJson(scenario) {
  const json = scenarioToJsonString(scenario);
  const blob = new Blob([json], { type: "application/json;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = scenarioFilename(scenario);
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function formatApiError(err) {
  if (!err || typeof err !== "object") {
    return String(err);
  }
  if (Array.isArray(err.detail)) {
    return err.detail
      .map((item) => {
        const path = item.loc?.slice(1).join(".") || "root";
        return `${path}: ${item.msg}`;
      })
      .join("\n");
  }
  return err.detail || err.message || JSON.stringify(err);
}

export async function validateScenarioJson(api, raw) {
  const parsed = typeof raw === "string" ? parseScenarioJsonText(raw) : raw;
  return api("/scenarios/validate", {
    method: "POST",
    body: JSON.stringify(parsed),
  });
}
