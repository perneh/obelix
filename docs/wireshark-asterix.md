# Wireshark with ASTERIX

Capture and decode **ASTERIX** traffic sent by Obelix.

**Prerequisites:** Wireshark 3.x+ installed — see [Wireshark installation](wireshark-install.md).

> **Obelix default UDP port:** `8600` (configurable in the UI and via Docker).

Modern Wireshark includes a **built-in ASTERIX dissector** — no separate plugin is needed for Wireshark 3.x / 4.x. See the [Wireshark ASTERIX wiki](https://wiki.wireshark.org/ASTERIX).

---

## Configure ASTERIX in Wireshark

The dissector cannot guess category **editions**. Set versions to match what Obelix sends.

1. Open **Wireshark → Preferences** (macOS: **Wireshark → Settings**)
2. Go to **Protocols → ASTERIX**
3. Set edition/version for each category you use:

| Category | Obelix edition | Wireshark preference (approx.) |
|----------|----------------|--------------------------------|
| 015 | 1.1 | Cat 015 → matching edition |
| 016 | 1.0 | Cat 016 → matching edition |
| 021 | 2.7 | Cat 021 → matching edition |
| 034 | 1.29 | Cat 034 → matching edition |
| 048 | 1.32 | Cat 048 → matching edition |
| 062 | 1.21 | Cat 062 → matching edition |
| 065 | 1.5 | Cat 065 → matching edition |
| 240 | 1.3 | Cat 240 → matching edition |

4. Click **OK**

If fields decode incorrectly, try the closest available edition in the dropdown. See [Wireshark ASTERIX preferences](https://wiki.wireshark.org/ASTERIX#preference-settings).

### Verify ASTERIX dissector

```bash
tshark -G protocols | grep -i asterix
```

You should see `asterix` and `asterix-tcp` in the output.

---

## Capture Obelix ASTERIX traffic

### Docker (recommended for Obelix users)

See **[Wireshark + Docker use case](wireshark-docker-usecase.md)** for a full walkthrough: start `./obelix start --dev --tools`, send to `obelix-udp-receiver`, capture on the Docker bridge interface, and decode Cat 034/048/062.

### Local setup (without Docker)

#### 1. Start Obelix

```bash
./obelix start --dev
# Optional built-in UDP listener on port 8600:
./obelix start --dev --tools
```

#### 2. Start capture in Wireshark

- **Interface:** loopback (`Loopback: lo0` on macOS, `Loopback` on Windows, `lo` on Linux) when sending to `127.0.0.1`
- **Capture filter:** `udp port 8600`

Or capture on your Ethernet/Wi‑Fi interface if traffic goes to another host.

#### 3. Send from Obelix

In the **Message Editor** tab: configure host `127.0.0.1`, port `8600`, click **Send via UDP**.

#### 4. Inspect packets

In the packet list you should see UDP payloads decoded as **ASTERIX**, for example:

```text
ASTERIX packet, Category 062
    Category: 62
    Length: …
    FSPEC
    010, Data Source Identifier
    …
```

---

## Display filters

| Filter | Purpose |
|--------|---------|
| `asterix` | All ASTERIX packets |
| `asterix.category == 62` | Category 062 only |
| `asterix.category == 34` | Category 034 only |
| `asterix.category == 48` | Category 048 only |
| `udp.port == 8600 && asterix` | Obelix default port + ASTERIX |

Examples from the [Wireshark wiki](https://wiki.wireshark.org/ASTERIX#display-filter): `asterix.SAC == 1`, `asterix.category == 62 && asterix.AI == "CALLSIGN"`.

---

## Command-line capture

```bash
# Capture 10 packets to file
tshark -i lo -f "udp port 8600" -c 10 -w obelix-asterix.pcapng

# Read and decode ASTERIX
tshark -r obelix-asterix.pcapng -Y asterix
```

Replace `-i lo` with the correct interface (`tshark -D` lists interfaces).

---

## Compare Obelix hex with Wireshark

1. In Obelix, click **Generate Hex** and copy the hex string
2. In Wireshark, select the UDP packet → **Packet Bytes** pane
3. Compare bytes — they should match (Obelix sends raw ASTERIX datablocks, no extra header)

---

## Troubleshooting

| Problem | Suggested fix |
|---------|----------------|
| No ASTERIX decode, only “UDP payload” | Upgrade to Wireshark 3.x+; enable **Protocols → ASTERIX** |
| Wrong field values | Set correct category **edition** in ASTERIX preferences |
| No packets on loopback | Use loopback interface; confirm Obelix sends to `127.0.0.1:8600` |
| Docker: no packets | See [Wireshark + Docker](wireshark-docker-usecase.md); avoid `127.0.0.1` from container |
| Capture permission errors | See [Wireshark installation — troubleshooting](wireshark-install.md#general-troubleshooting) |

---

## References

- [Wireshark installation](wireshark-install.md)
- [Wireshark ASTERIX wiki](https://wiki.wireshark.org/ASTERIX)
- [Eurocontrol ASTERIX publications](https://www.eurocontrol.int/asterix)
- [Obelix usage guide](usage.md)
- Per-category notes: [docs/categories/](categories/README.md)
