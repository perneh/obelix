# Link 16 scenario library

Pre-built realistic Link 16 J-message exercise scenarios for Obelix.

| File | Description |
|------|-------------|
| `shared/jas-uppsala-visby.json` | JAS 39 training transit Uppsala/Arlanda → Visby |
| `shared/jas-dogfight-mig-gotland.json` | 2× JAS vs 4× MiG-29 dogfight over Gotland |
| `shared/jas-f16-marking-fi.json` | 2× JAS + 2× F-16 marking run vs Finnish sector |
| `shared/c2-bilateral-stric-fi.json` | Bilateral C2 exchange Swedish STRIC ↔ Finnish CRC |
| `shared/c2-network-mesh.json` | Five-node C2 mesh (SE, FI, EE, NATO CAOC, AWACS) |

## Participant JU map

| Source JU | Role |
|-----------|------|
| 10001 | Swedish STRIC / CRC |
| 10002 | Finnish CRC |
| 10003 | Estonian CRC |
| 10004 | NATO CAOC |
| 10005 | AWACS relay |
| 11001–11002 | JAS 39 Gripen |
| 12001–12004 | MiG-29 (hostile tracks) |
| 13001–13002 | F-16 |

Scenarios use J2.3 PPLI, J3.2 air tracks, J0.x network management, J10.x engagement, J11.0 EW, J12.x mission/text, J14.0 parametric, and J15.0 simulation management.

Custom scenarios saved from the UI go to `data/link16_scenarios/` (local, gitignored). Copy JSON into `scenarios/link16/shared/` and commit to add variants to the library.

Default transport: UDP port **8700** (JREAP). See [Wireshark & Link 16](../docs/wireshark-link16.md).
