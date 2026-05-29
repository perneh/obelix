# Architecture

Obelix is a web-based tool for creating, editing and sending ASTERIX messages. It consists of a FastAPI backend, a static browser frontend, and JSON file storage for templates and scenarios.

## Architecture diagram

```mermaid
flowchart TB
    subgraph Browser["Browser"]
        UI["Frontend<br/>(HTML / CSS / JS)"]
    end

    subgraph Backend["FastAPI backend"]
        API["REST API<br/>categories · encode · send · scenarios · storage"]
        REG["Category registry<br/>(plugin pattern)"]
        ENC["ASTERIX encoder<br/>FSPEC · data items · hex"]
        RUN["Scenario runner<br/>async · timing · pause/stop"]
        TRN["Transport<br/>UDP / TCP"]
        STO["Storage<br/>JSON files"]
        MDL["Pydantic models"]
    end

    subgraph Categories["ASTERIX categories"]
        C34["Cat 034<br/>Monoradar Service"]
        C48["Cat 048<br/>Monoradar Target"]
    end

    subgraph Persistence["File storage"]
        TPL[("data/templates/")]
        SCN[("data/scenarios/")]
    end

    subgraph External["External systems"]
        RX["UDP / TCP receiver<br/>e.g. radar simulator"]
    end

    UI -->|"HTTP REST"| API
    API --> MDL
    API --> REG
    API --> ENC
    API --> RUN
    API --> TRN
    API --> STO

    REG --> C34
    REG --> C48
    C34 --> ENC
    C48 --> ENC

    RUN --> ENC
    RUN --> TRN
    TRN -->|"binary ASTERIX"| RX

    STO --> TPL
    STO --> SCN

    REG -.->|"field schema"| API
    API -.->|"JSON schema"| UI
```

### Request flow (encode & send)

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
    User->>UI: Generate Hex / Send
    UI->>API: POST /api/encode or /api/send
    API->>REG: Resolve category
    REG->>ENC: encode_datablock(fields)
    ENC-->>API: bytes / hex

    alt Generate Hex
        API-->>UI: hex + length
        UI-->>User: Show preview
    else Send message
        API->>TRN: UDP or TCP
        TRN->>RX: ASTERIX datablock
        API-->>UI: success + bytes sent
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

## Supported categories (v0.1)

| Category | Name | Edition |
|----------|------|---------|
| 015 | INCS Target Reports | 1.1 |
| 016 | INCS Configuration Reports | 1.0 |
| 034 | Monoradar Service Messages | 1.29 |
| 048 | Monoradar Target Reports | 1.32 |
| 062 | System Track Data | 1.21 |
