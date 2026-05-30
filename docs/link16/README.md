# Link 16 J-message reference

Obelix implements Link 16 J-series messages as encoders with matching UI forms, parallel to ASTERIX categories.

## Architecture

| Layer | Description |
|-------|-------------|
| **J-message plugins** | One encoder per J-series label (`J3.2`, `J2.2`, …) |
| **Field schema** | Same `FieldDefinition` model as ASTERIX — drives UI and OpenAPI |
| **JREAP-C simple** | Messages wrapped for UDP/TCP simulation (magic `JREA`) |
| **Default port** | `8700` (ASTERIX uses `8600`) |

## Supported J-series (38 messages)

| Family | Messages |
|--------|----------|
| **J0** | J0.0, J0.1, J0.2, J0.3 |
| **J2** | J2.0, J2.2, J2.3, J2.4, J2.5, J2.6 |
| **J3** | J3.0–J3.6 |
| **J7** | J7.0, J7.1, J7.2, J7.4, J7.5 |
| **J9** | J9.0, J9.1, J9.2 |
| **J10** | J10.0, J10.1 |
| **J11** | J11.0 |
| **J12** | J12.0, J12.1, J12.2, J12.4, J12.5, J12.6 |
| **J13** | J13.0, J13.2 |
| **J14** | J14.0 |
| **J15** | J15.0 |

## API

| Endpoint | Purpose |
|----------|---------|
| `GET /api/link16/messages` | List all J-messages |
| `GET /api/link16/messages/{J3-2}` | Full field schema |
| `GET /api/link16/messages/{J3-2}/help` | Markdown help |
| `POST /api/link16/encode` | Encode to hex |
| `POST /api/link16/send` | Generic send |
| `POST /api/link16/send/{J3-2}` | Typed send with Swagger example |

## Simulating multiple C2 nodes

Set **Source JU** on each message to simulate different Link 16 participants (e.g. 10001 = CRC, 10002 = fighter). Run multiple scenarios or steps with different source JUs targeting the same gateway port.

Capture in Wireshark: [Wireshark & Link 16](../wireshark-link16.md) (port **8700**).

## Adding a J-message

1. Add fields in `backend/app/link16/messages/` (or use `make_j_message_class`)
2. Register in the family module and `registry.py`
3. Add help under `docs/link16/{j3-2}.md`
4. Add unit/regression tests

Reference: [STANAG 5516](https://www.nato.int/) Link 16 tactical data link.
