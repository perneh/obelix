# Architecture

Obelix is a web-based tool for creating, editing and sending ASTERIX messages. It consists of a FastAPI backend, a static browser frontend, and JSON file storage for templates and scenarios.

## Architecture diagram

```mermaid
flowchart TB
    subgraph browser [Browser]
        ui[Frontend UI]
    end

    subgraph backend [FastAPI backend]
        api[REST API]
        reg[Category registry]
        enc[ASTERIX encoder]
        run[Scenario runner]
        trn[UDP and TCP transport]
        sto[JSON storage]
    end

    subgraph plugins [Category plugins]
        direction LR
        c015[015]
        c016[016]
        c021[021]
        c034[034]
        c048[048]
        c062[062]
        c065[065]
        c240[240]
    end

    subgraph disk [File storage]
        cfg[(configurations)]
        scn[(scenarios)]
    end

    rx[(External receiver)]

    ui -->|HTTP| api
    api --> reg
    api --> enc
    api --> run
    api --> trn
    api --> sto
    reg --> plugins
    plugins --> enc
    run --> enc
    run --> trn
    trn -->|ASTERIX binary| rx
    sto --> cfg
    sto --> scn
    reg -.->|field schema| api
    api -.->|JSON schema| ui
```

### Request flow (encode and send)

```mermaid
sequenceDiagram
    actor User
    participant UI as Frontend
    participant API as REST API
    participant REG as Registry
    participant ENC as Encoder
    participant TRN as Transport
    participant RX as Receiver

    User->>UI: Edit fields
    User->>UI: Generate Hex or Send
    UI->>API: POST /api/encode or /api/send
    API->>REG: Resolve category
    REG->>ENC: encode_datablock
    ENC-->>API: bytes and hex

    alt Generate Hex only
        API-->>UI: hex and length
        UI-->>User: Show preview
    else Send message
        API->>TRN: UDP or TCP payload
        TRN->>RX: ASTERIX datablock
        API-->>UI: success and bytes_sent
        UI-->>User: Confirm send
    end
```

## Project structure

```
obelix/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── api/                    # REST API route handlers
│   │   ├── asterix/                # ASTERIX encoding framework
│   │   │   ├── base.py             # Field schema, FSPEC builder, base encoder
│   │   │   ├── registry.py         # Category registry (plugin pattern)
│   │   │   └── categories/         # One module per ASTERIX category
│   │   ├── core/                   # Config, scenario runner, file storage
│   │   ├── models/                 # Pydantic request/response models
│   │   └── transport/              # UDP/TCP sending
│   └── tests/
├── frontend/                       # Static HTML/CSS/JS UI
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
└── data/                           # Saved templates and scenarios (JSON)
    ├── templates/
    └── scenarios/
```

## Design decisions

1. **Category plugin pattern** – Each ASTERIX category is a class implementing `definition()` (field schema for the UI) and `encode_record()` (binary encoding). Register new categories in `registry.py`.

2. **Schema-driven UI** – The frontend builds forms dynamically from the category field definitions returned by the API. No frontend changes needed when adding a category.

3. **Separation of concerns** – Encoding (`asterix/`), transport (`transport/`), orchestration (`scenario_runner.py`), and persistence (`storage.py`) are independent modules.

4. **Async scenario runner** – Scenarios run as background asyncio tasks with pause/stop via events, supporting configurable delays, repetition, and looping.

## Supported categories

| Category | Name | Edition |
|----------|------|---------|
| 015 | INCS Target Reports | 1.1 |
| 016 | INCS Configuration Reports | 1.0 |
| 021 | ADS-B Reports | 2.7 |
| 034 | Monoradar Service Messages | 1.29 |
| 048 | Monoradar Target Reports | 1.32 |
| 062 | System Track Data | 1.21 |
| 065 | SDPS Service Status | 1.5 |
| 240 | Radar Video Transmission | 1.3 |
