# Wireshark installation

General guide for installing Wireshark on macOS, Ubuntu, Red Hat, and Windows. Use Wireshark **3.x or 4.x**.

For protocol-specific capture and decode guides after installation:

| Guide | Purpose |
|-------|---------|
| [Wireshark & ASTERIX](wireshark-asterix.md) | ASTERIX traffic from Obelix (port 8600) |
| [Wireshark & Link 16](wireshark-link16.md) | Link 16 JREAP from Obelix (port 8700) |
| [Wireshark + Docker](wireshark-docker-usecase.md) | ASTERIX from Obelix Docker containers |

---

## macOS

### Option A — Homebrew (recommended for developers)

```bash
brew install --cask wireshark
brew install wireshark   # optional: tshark, capinfos, …
```

### Option B — Official installer

1. Download the latest `.dmg` from [https://www.wireshark.org/download.html](https://www.wireshark.org/download.html)
2. Drag **Wireshark** to Applications
3. Run **Install ChmodBPF** from the disk image (or from `/Applications/Wireshark.app`) so non-root users can capture packets
4. Log out and back in if prompted

### Capture permissions

If capture fails with a permission error:

```bash
ls -l /dev/bpf*
```

After **Install ChmodBPF**, your user should have access; otherwise approve when macOS asks for admin rights.

---

## Ubuntu (and Debian-based Linux)

```bash
sudo apt update
sudo apt install wireshark wireshark-common tshark
```

When asked whether non-superusers may capture packets, select **Yes**. If you missed that step:

```bash
sudo dpkg-reconfigure wireshark-common
sudo usermod -aG wireshark "$USER"
# Log out and back in
```

Optional GUI launcher:

```bash
sudo apt install wireshark-qt
```

---

## Red Hat Enterprise Linux / Fedora / Rocky / AlmaLinux

### Fedora / RHEL 8+ / Rocky / Alma

```bash
sudo dnf install wireshark wireshark-cli
sudo dnf install wireshark-gnome   # GUI on Fedora
# or: sudo dnf install wireshark-qt
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

If the `wireshark` group does not exist:

```bash
sudo groupadd wireshark
sudo usermod -aG wireshark "$USER"
sudo chmod 750 /usr/bin/dumpcap
sudo chgrp wireshark /usr/bin/dumpcap
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap
```

---

## Windows

1. Download the installer from [https://www.wireshark.org/download.html](https://www.wireshark.org/download.html)
2. Run the `.exe` as Administrator
3. Install **Npcap** (recommended) when prompted
4. Complete the setup wizard with default options unless you have specific needs

Run Wireshark as a normal user; approve the Npcap driver if Windows asks.

---

## Verify installation

All platforms:

```bash
wireshark -v
tshark -D    # list capture interfaces
```

Confirm version ≥ 3.0 (**Help → About Wireshark** on Windows/macOS GUI).

Optional — list available dissectors:

```bash
tshark -G protocols | grep -i asterix
tshark -G protocols | grep -i jreap
```

---

## General troubleshooting

| Problem | Suggested fix |
|---------|----------------|
| Permission denied (Linux) | Add user to `wireshark` group; log out and back in |
| Permission denied (macOS) | Run **Install ChmodBPF** from the Wireshark bundle |
| No capture (Windows) | Reinstall **Npcap**; run Wireshark installer as Admin |
| No interfaces listed | Run `tshark -D`; on Linux check group membership |
| Empty capture | Start capture **before** sending traffic; confirm host/port and interface |

Protocol-specific decode issues are covered in [Wireshark & ASTERIX](wireshark-asterix.md) and [Wireshark & Link 16](wireshark-link16.md).

---

## References

- [Wireshark downloads](https://www.wireshark.org/download.html)
- [Wireshark documentation](https://www.wireshark.org/docs/)
