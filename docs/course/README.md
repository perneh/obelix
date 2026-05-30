# Obelix guided course

Step-by-step walkthrough of the Obelix web UI and REST API. Screenshots were captured automatically with [Playwright](https://playwright.dev/) while the dev server was running on `localhost:8000`.

**Prerequisites:** start Obelix before following along:

```bash
./obelix start --dev
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## Part 1 — Getting oriented

Obelix supports two tactical data link protocols from one application:

| Protocol | Default UDP port | Typical use |
|----------|------------------|-------------|
| **ASTERIX** | 8600 | Surveillance track reports (Cat 015, 021, 048, …) |
| **Link 16** | 8700 | J-series JREAP messages (J2 PPLI, J3 tracks, J12 mission, …) |

The header bar has two dropdown menus — **ASTERIX** and **Link 16** — each with three views:

- **Message Editor** — compose and send a single message
- **Scenario Builder** — chain steps with delays, loops, and (for ASTERIX) route animation
- **Configurations & Scenarios** — load saved templates and pre-built exercises

On first load you land on the ASTERIX Message Editor:

![Home — ASTERIX Message Editor](images/01-home-asterix-message.png)

Click a dropdown to switch protocol and view:

![Navigation dropdown — ASTERIX menu](images/02-nav-dropdown-asterix.png)

---

## Part 2 — ASTERIX Message Editor

1. Choose **ASTERIX → Message Editor**.
2. Pick a category in the sidebar (e.g. Cat 048 — Monoradar Target Report).
3. Edit field values in the form.
4. Click **Generate Hex** to encode the message without sending it.
5. Set host/port (default port **8600**) and click **Send via UDP** or **Send via TCP**.

![ASTERIX — encoded hex preview](images/03-asterix-encode-hex.png)

The hex panel shows the binary payload you would inject into a UDP/TCP stream. Use this to verify field values before sending to a receiver or Wireshark.

**REST equivalent:** `POST /api/encode` and `POST /api/send/{category}` — see [Part 5](#part-5--rest-api-swagger).

---

## Part 3 — ASTERIX Scenario Builder

Scenarios let you send a sequence of messages with timing control.

1. Configure a message in **Message Editor**.
2. Switch to **ASTERIX → Scenario Builder**.
3. Click **Add Step from Current Message**.
4. Set per-step delay, repeat count, loop count, and interval.
5. For moving tracks (Cat 015, 021, 034, 048, 062, 240): enable **Animate route** and configure waypoints.
6. Click **Start**; use **Pause**, **Resume**, and **Stop** during execution.

![ASTERIX Scenario Builder — step list and controls](images/04-asterix-scenario-builder.png)

Each step appears in the timeline on the left. Transport settings (host, port, protocol) apply to the whole run.

### Export and import JSON

Use **Download .json file** or **Save locally & download** to persist a scenario. **Import .json file** validates the file via `POST /api/scenarios/validate` before loading it into the builder.

![ASTERIX scenario JSON panel](images/05-asterix-scenario-json.png)

Pre-built Baltic exercise scenarios live in [`scenarios/shared/`](../../scenarios/shared/). Load them from the library (next section).

---

## Part 4 — ASTERIX Configurations & Scenarios

**ASTERIX → Configurations & Scenarios** is the library for saved field setups and scenario files.

![ASTERIX library — configurations and saved scenarios](images/06-asterix-library.png)

| Action | What it does |
|--------|----------------|
| **Load** on a configuration | Applies saved field values to Message Editor |
| **Load** on a scenario | Opens the scenario in Scenario Builder |
| **Export** | Downloads the scenario JSON |
| **Import .json file** | Adds a scenario to local storage |

Configurations are stored under `data/configurations/`; scenarios under `data/scenarios/`. Both can be version-controlled via git — see [`configurations/README.md`](../../configurations/README.md).

---

## Part 5 — Link 16 Message Editor

Switch to **Link 16 → Message Editor** to work with J-series messages wrapped in JREAP.

1. Select a J-message family and variant (e.g. **J3.2 — Air Track**).
2. Edit fields — note **Source JU** to simulate different C2 participants.
3. Click **Generate Hex** for a JREAP preview.
4. Send on port **8700** (default).

![Link 16 Message Editor — J3.2 Air Track](images/07-link16-message-editor.png)

### In-app help

Click **Help** to open the field reference for the selected J-message. Content comes from [`docs/link16/`](../../link16/) when available, or is auto-generated from the message schema.

![Link 16 help panel — J3.2 field reference](images/08-link16-help-panel.png)

**REST equivalent:** `GET /api/link16/messages`, `POST /api/link16/encode`, `POST /api/link16/send/{j_series}`.

---

## Part 6 — Link 16 Scenario Builder

The Link 16 scenario workflow mirrors ASTERIX:

1. Configure a J-message and click **Add to Scenario →**.
2. Open **Link 16 → Scenario Builder**.
3. Review steps, set transport (port **8700**), loop count, and interval.
4. **Start Scenario** to send steps in order.

![Link 16 Scenario Builder](images/09-link16-scenario-builder.png)

Use different **Source JU** values on consecutive steps to simulate a multi-node exercise (e.g. two C2 sites and a fighter).

Pre-built Link 16 exercises are in [`scenarios/link16/shared/`](../../scenarios/link16/shared/) — JAS transit, dogfight, marking run, C2 bilateral, and C2 mesh scenarios.

Export/import JSON works the same way as ASTERIX (`POST /api/link16/scenarios/validate`).

---

## Part 7 — Link 16 Configurations & Scenarios

![Link 16 library](images/10-link16-library.png)

Load shared scenarios such as `jas-uppsala-visby` or `c2-mesh-five-node` directly into the Scenario Builder. Saved local scenarios and configurations appear here after you save from the editor or builder.

---

## Part 8 — REST API (Swagger)

Obelix exposes a FastAPI backend. Interactive documentation is at [http://localhost:8000/docs](http://localhost:8000/docs).

![Swagger UI — API overview](images/11-swagger-overview.png)

### ASTERIX send endpoints

Each implemented category has a typed endpoint with example values:

![Swagger — POST /api/send/{category}](images/12-swagger-asterix-send.png)

Example request body:

```json
{
  "fields": { "..." : "category-specific defaults" },
  "host": "host.docker.internal",
  "port": 8600,
  "protocol": "udp"
}
```

| Category | Endpoint |
|----------|----------|
| 015 | `POST /api/send/15` |
| 016 | `POST /api/send/16` |
| 021 | `POST /api/send/21` |
| 034 | `POST /api/send/34` |
| 048 | `POST /api/send/48` |
| 062 | `POST /api/send/62` |
| 065 | `POST /api/send/65` |
| 240 | `POST /api/send/240` |

Use the generic `POST /api/send` when the category is embedded inside a `message` object.

### Link 16 endpoints

![Swagger — POST /api/link16/send/{j_series}](images/13-swagger-link16-send.png)

List available J-messages and their field schemas:

![Swagger — GET /api/link16/messages](images/14-swagger-link16-messages.png)

Try **Execute** in Swagger to send a test message to your local UDP listener on port 8700.

---

## Part 9 — Verify with Wireshark

After sending messages, capture traffic on the appropriate port:

| Protocol | Port | Guide |
|----------|------|-------|
| ASTERIX | 8600 | [Wireshark & ASTERIX](../wireshark-asterix.md) |
| Link 16 | 8700 | [Wireshark & Link 16](../wireshark-link16.md) |

Filter examples:

```
udp.port == 8600
udp.port == 8700
```

---

## Part 10 — Automated frontend tests

Obelix includes Playwright regression tests that exercise the same UI flows shown in this course:

```bash
pip install -e ".[dev]"
playwright install chromium
./obelix start --dev   # separate terminal
./scripts/test.sh frontend --address=localhost --port=8000
```

See [backend/tests/README.md](../../backend/tests/README.md) for details.

### Regenerate course screenshots

When the UI changes, re-capture all images:

```bash
./obelix start --dev
python scripts/capture_course_screenshots.py --base-url http://localhost:8000
```

Output is written to `docs/course/images/`.

---

## Next steps

| Topic | Document |
|-------|----------|
| Full usage reference | [docs/usage.md](../usage.md) |
| Architecture overview | [docs/architecture.md](../architecture.md) |
| ASTERIX category help | [docs/categories/README.md](../categories/README.md) |
| Link 16 J-message reference | [docs/link16/README.md](../link16/README.md) |
| Development & testing | [docs/development.md](../development.md) |
