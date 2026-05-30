# Wireshark with Link 16

Capture and inspect **Link 16 JREAP** traffic sent by Obelix.

**Prerequisites:** Wireshark 3.x+ installed — see [Wireshark installation](wireshark-install.md).

> **Obelix default Link 16 UDP port:** `8700` (ASTERIX uses `8600`).

---

## What Obelix sends

Obelix wraps each J-message in a **JREAP-C simple** envelope for lab/simulation over UDP or TCP. This is **not** bit-exact STANAG JREAP over a MIDS terminal — it is designed for C2 gateway testing and packet inspection.

### Packet layout (24-byte header + payload)

| Offset | Size | Field |
|--------|------|--------|
| 0 | 4 | Magic `JREA` (`4A524541` in hex) |
| 4 | 1 | Version (`1`) |
| 5 | 1 | J-series label length |
| 6 | 2 | NPG (big-endian) |
| 8 | 4 | Source JU (big-endian) |
| 12 | 4 | Payload length (big-endian) |
| 16 | 8 | J-series ASCII (e.g. `J3.2`, null-padded) |
| 24 | n | J-message payload |

Wireshark may **not** decode this as Link 16 automatically — you will often see **UDP** with a payload starting with `4A524541`. Use the hex view and compare with Obelix **Generate Hex** in the **Link 16** tab.

---

## Capture Obelix Link 16 traffic

### Local setup

#### 1. Start Obelix

```bash
./obelix start --dev
```

#### 2. Start capture in Wireshark

- **Interface:** loopback when sending to `127.0.0.1`
- **Capture filter:** `udp port 8700`

#### 3. Send from Obelix

Open the **Link 16** tab, select a J-message (e.g. **J3.2 Air Track**), set host/port, click **Send via UDP**.

Default transport in the Link 16 tab: `host.docker.internal:8700` (change to `127.0.0.1` for local loopback capture).

### Docker

Same principles as ASTERIX — see [Wireshark + Docker use case](wireshark-docker-usecase.md), but use port **8700** and the **Link 16** tab.

| Send target in UI | Where packets go | Wireshark interface |
|-------------------|------------------|---------------------|
| `host.docker.internal` | Host loopback (macOS/Windows Docker) | Loopback |
| `127.0.0.1` inside container | Container loopback (often invisible on host) | Avoid — use `host.docker.internal` |
| Another container hostname | Docker bridge | `docker0` / `bridge100` |

---

## Display and capture filters

| Filter | Purpose |
|--------|---------|
| `udp.port == 8700` | All Obelix Link 16 traffic |
| `udp.port == 8700 && frame contains JREA` | Packets with Obelix JREAP magic |
| `udp.port == 8700 && frame contains "J3.2"` | J3.2 air track (adjust J-series as needed) |

If your Wireshark build includes a **JREAP** or **Link 16** dissector, check **Protocols** preferences — it may expect standard JREAP framing, not Obelix’s simplified header. When in doubt, use **Packet Bytes** and manual inspection.

---

## Inspect packets manually

1. Select a UDP packet on port 8700
2. Expand **User Datagram Protocol** → note source/destination ports
3. Open **Packet Bytes** — confirm:
   - Bytes 0–3: `4A 52 45 41` (`JREA`)
   - Bytes 16–23: J-series label (e.g. `4A 33 2E 32` = `J3.2`)
4. Compare full hex with Obelix **Generate Hex** output

Example first bytes for J3.2 (will vary with field values):

```text
4A524541  …  JREA magic
…           …  source JU, NPG, length
4A332E32    …  "J3.2" in header
…           …  encoded J-message body
```

---

## Command-line capture

```bash
tshark -i lo -f "udp port 8700" -c 10 -w obelix-link16.pcapng
tshark -r obelix-link16.pcapng -Y "udp.port == 8700"
tshark -r obelix-link16.pcapng -x   # hex dump
```

---

## Simulating multiple C2 nodes

Each message includes **Source JU** in the JREAP header. Filter or inspect that field in hex (offset 8–11, big-endian uint32) to distinguish simulated participants (e.g. 10001 vs 10002).

---

## Troubleshooting

| Problem | Suggested fix |
|---------|----------------|
| No packets | Capture filter `udp port 8700`; start capture before send |
| No Link 16 decode tree | Expected for Obelix JREAP-simple — use hex compare |
| Wrong interface (Docker) | Same as ASTERIX — see [Docker use case](wireshark-docker-usecase.md) |
| Hex mismatch | Regenerate hex in Obelix; confirm same J-message and field values |
| Permission denied | See [Wireshark installation — troubleshooting](wireshark-install.md#general-troubleshooting) |

---

## References

- [Wireshark installation](wireshark-install.md)
- [Link 16 reference](link16/README.md)
- [Obelix usage — Link 16](usage.md#link-16-j-messages)
- [STANAG 5516](https://www.nato.int/) Link 16 (full tactical datalink specification)
