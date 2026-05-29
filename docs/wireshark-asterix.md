# Wireshark with ASTERIX

Guide for installing Wireshark on macOS, Ubuntu, Red Hat, and Windows, and using it to inspect ASTERIX traffic from Obelix.

Modern Wireshark includes a **built-in ASTERIX dissector** — you do not need a separate plugin for Wireshark 3.x / 4.x. See the [Wireshark ASTERIX wiki](https://wiki.wireshark.org/ASTERIX) for details.

> **Obelix default UDP port:** `8600` (configurable in the UI and via `OBELIX_UDP_PORT` in Docker).

---

## macOS

### Option A — Homebrew (recommended for developers)

```bash
# Install Wireshark GUI
brew install --cask wireshark

# Optional: command-line tools (tshark, capinfos, …)
brew install wireshark
```

### Option B — Official installer

1. Download the latest `.dmg` from [https://www.wireshark.org/download.html](https://www.wireshark.org/download.html)
2. Open the disk image and drag **Wireshark** to Applications
3. Run **Install ChmodBPF** from the disk image (or from `/Applications/Wireshark.app`) so non-root users can capture packets
4. Log out and back in if prompted

### Capture permissions

If capture fails with a permission error:

```bash
# After running Install ChmodBPF once:
ls -l /dev/bpf*
# Your user should be in group access; otherwise run Wireshark with admin approval when macOS asks.
```

### Verify ASTERIX support

```bash
wireshark -v
tshark -G protocols | grep -i asterix
```

You should see `asterix` and `asterix-tcp` in the output.

---

## Ubuntu (and Debian-based Linux)

### Install

```bash
sudo apt update
sudo apt install wireshark wireshark-common tshark
```

During installation, select **Yes** when asked whether non-superusers should be allowed to capture packets. If you missed that step:

```bash
sudo dpkg-reconfigure wireshark-common
sudo usermod -aG wireshark "$USER"
# Log out and back in for group membership to apply
```

### Verify

```bash
wireshark -v
tshark -G protocols | grep -i asterix
```

### Optional — desktop launcher only

```bash
sudo apt install wireshark-qt   # if wireshark meta-package did not pull the GUI
```

---

## Red Hat Enterprise Linux / Fedora / Rocky / AlmaLinux

### Fedora / RHEL 8+ / Rocky / Alma

```bash
sudo dnf install wireshark wireshark-cli
```

GUI (if not included):

```bash
sudo dnf install wireshark-gnome   # Fedora
# or on some RHEL derivatives:
sudo dnf install wireshark-qt
```

### RHEL 7 (legacy)

```bash
sudo yum install wireshark wireshark-cli
```

### Capture permissions

```bash
sudo usermod -aG wireshark "$USER"
# Log out and back in
```

If the `wireshark` group does not exist, create it and adjust dumpcap:

```bash
sudo groupadd wireshark
sudo usermod -aG wireshark "$USER"
sudo chmod 750 /usr/bin/dumpcap
sudo chgrp wireshark /usr/bin/dumpcap
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap
```

### Verify

```bash
wireshark -v
tshark -G protocols | grep -i asterix
```

---

## Windows

### Install

1. Download the installer from [https://www.wireshark.org/download.html](https://www.wireshark.org/download.html)
2. Run the `.exe` as Administrator
3. When prompted, install **Npcap** (recommended) or WinPcap for packet capture
4. Complete the setup wizard with default options unless you have specific needs

### Verify

Open **Wireshark → Help → About Wireshark** and confirm version ≥ 3.0.

Command prompt:

```cmd
"C:\Program Files\Wireshark\tshark.exe" -G protocols | findstr /i asterix
```

### Notes

- Run Wireshark as a normal user; approve the Npcap driver if Windows asks
- External ASTERIX plugins (e.g. legacy Croatia Control builds) are **obsolete** for Wireshark ≥ 1.10 — use the built-in dissector instead

---

## Configure ASTERIX in Wireshark

The dissector cannot guess category **editions**. Set versions to match what Obelix sends.

1. Open **Wireshark → Preferences** (macOS: **Wireshark → Settings**)
2. Go to **Protocols → ASTERIX**
3. Set edition/version for each category you use:

| Category | Obelix edition | Wireshark preference (approx.) |
|----------|----------------|--------------------------------|
| 034 | 1.29 | Cat 034 → matching edition |
| 048 | 1.32 | Cat 048 → matching edition |
| 062 | 1.21 | Cat 062 → matching edition |

4. Click **OK**

If fields decode incorrectly, try the closest available edition in the dropdown. See [Wireshark ASTERIX preferences](https://wiki.wireshark.org/ASTERIX#preference-settings).

---

## Capture Obelix traffic

### Docker (recommended for Obelix users)

See **[Wireshark + Docker use case](wireshark-docker-usecase.md)** for a full walkthrough: start `./obelix start --dev --tools`, send to `obelix-udp-receiver`, capture on the Docker bridge interface, and decode Cat 034/048/062.

### Local setup (without Docker)

#### 1. Start Obelix and a receiver (optional)

```bash
./obelix start --dev
# Optional built-in UDP listener on port 8600:
./obelix start --dev --tools
```

#### 2. Start capture in Wireshark

- **Interface:** loopback (`Loopback: lo0` on macOS, `Loopback` on Windows, `lo` on Linux) when sending to `127.0.0.1`
- **Capture filter:** `udp port 8600`

Or capture on your Ethernet/Wi‑Fi interface if traffic goes to another host.

#### 3. Send a message from Obelix

In the Obelix UI: configure host `127.0.0.1`, port `8600`, click **Send via UDP**.

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

### Useful display filters

| Filter | Purpose |
|--------|---------|
| `asterix` | All ASTERIX packets |
| `asterix.category == 62` | Category 062 only |
| `asterix.category == 34` | Category 034 only |
| `asterix.category == 48` | Category 048 only |
| `udp.port == 8600 && asterix` | Obelix default port + ASTERIX |

Examples from the [Wireshark wiki](https://wiki.wireshark.org/ASTERIX#display-filter): `asterix.SAC == 1`, `asterix.category == 62 && asterix.AI == "CALLSIGN"`.

### Command-line capture (all platforms)

```bash
# Capture 10 packets to file
tshark -i lo -f "udp port 8600" -c 10 -w obelix.pcapng

# Read and decode ASTERIX
tshark -r obelix.pcapng -Y asterix
```

Replace `-i lo` with the correct interface (`tshark -D` lists interfaces).

---

## Troubleshooting

| Problem | Suggested fix |
|---------|----------------|
| No ASTERIX decode, only “UDP payload” | Wireshark too old — upgrade to 3.x+; check **Protocols → ASTERIX** is enabled |
| Wrong field values | Set correct category **edition** in ASTERIX preferences |
| No packets on loopback | Use loopback interface; confirm Obelix sends to `127.0.0.1:8600` |
| Permission denied (Linux) | Add user to `wireshark` group; re-login |
| Permission denied (macOS) | Run **Install ChmodBPF** from Wireshark bundle |
| No capture (Windows) | Reinstall **Npcap**; run Wireshark installer as Admin |

---

## References

- [Wireshark downloads](https://www.wireshark.org/download.html)
- [Wireshark ASTERIX wiki](https://wiki.wireshark.org/ASTERIX)
- [Eurocontrol ASTERIX publications](https://www.eurocontrol.int/asterix)
- [Obelix usage guide](usage.md) — sending messages and UDP testing
