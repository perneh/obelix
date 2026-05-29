# Usage

## Usage diagram

```mermaid
flowchart TD
    START([Open Obelix in browser]) --> TAB{Choose tab}

    TAB -->|Message Editor| CAT[Select ASTERIX category]
    CAT --> FORM[Edit message fields]
    FORM --> MA{Choose action}

    MA -->|Generate Hex| HEX[Preview hex / binary output]
    MA -->|Send| CFG[Set host, port, UDP or TCP]
    CFG --> SEND[Send single message]
    SEND --> RX[(External receiver)]

    MA -->|Save as Template| SAVT[Save to data/templates/]

    TAB -->|Scenario Builder| STEP[Add steps from current message]
    STEP --> TIMING[Set delay, repeat, loop count, interval]
    TIMING --> SC{Scenario control}

    SC -->|Start| RUN[Scenario runner sends sequence]
    SC -->|Pause / Resume / Stop| RUN
    RUN --> RX

    TIMING --> SAVS[Save to data/scenarios/]

    TAB -->|Templates & Scenarios| LIB[Browse saved items]
    LIB -->|Load template| FORM
    LIB -->|Load scenario| TIMING

    SAVT --> LIB
    SAVS --> LIB
```

### Scenario execution flow

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Running: Start
    Running --> Paused: Pause
    Paused --> Running: Resume
    Running --> Stopped: Stop
    Running --> Completed: All loops finished
    Paused --> Stopped: Stop
    Stopped --> [*]
    Completed --> [*]

    state Running {
        [*] --> NextStep
        NextStep --> WaitDelay: delay_ms > 0
        WaitDelay --> Encode
        NextStep --> Encode: no delay
        Encode --> SendRepeat: repeat N times
        SendRepeat --> NextStep: more steps
        SendRepeat --> LoopWait: scenario loop
        LoopWait --> NextStep: interval elapsed
    }
```

## Message editor

1. Select an ASTERIX category from the sidebar.
2. Edit field values in the form.
3. Click **Generate Hex** to preview the encoded binary data.
4. Configure host/port and click **Send via UDP** (or TCP).

## Scenario builder

1. Configure messages in the Message Editor tab.
2. Switch to **Scenario Builder** and click **Add Step from Current Message**.
3. Set delays, repeats, loop count and interval.
4. Click **Start** to run; use **Pause**, **Resume**, and **Stop** to control execution.

## Templates and scenarios

Save message templates and scenarios from the UI. They are stored as JSON files under `data/templates/` and `data/scenarios/`.

## Testing a UDP receiver

When running with `./obelix start --tools`, a UDP listener is started automatically on port 8600.

For decoding ASTERIX in Wireshark (install, capture filters, edition settings), see [Wireshark & ASTERIX](wireshark-asterix.md).

**Docker use case:** step-by-step capture of container traffic → [Wireshark + Docker use case](wireshark-docker-usecase.md).

To listen manually without Docker:

```bash
python -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 8600))
print('Listening on UDP 8600...')
while True:
    data, addr = s.recvfrom(4096)
    print(f'{addr}: {data.hex().upper()}')
"
```
