# Obelix

Web-based tool for creating, editing and sending ASTERIX messages.

## Quick start

```bash
chmod +x obelix
./obelix start --dev
```

Open [http://localhost:8000](http://localhost:8000) — API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

## Documentation

| Topic | Description |
|-------|-------------|
| [Architecture](docs/architecture.md) | Project structure, design decisions, supported ASTERIX categories |
| [Setup](docs/setup.md) | Docker and local installation |
| [Usage](docs/usage.md) | Message editor, scenarios, templates, UDP testing |
| [Wireshark & ASTERIX](docs/wireshark-asterix.md) | Install Wireshark on macOS, Ubuntu, Red Hat, Windows |
| [Wireshark + Docker](docs/wireshark-docker-usecase.md) | Decode ASTERIX from Obelix Docker containers |
| [Development](docs/development.md) | Tests, adding categories, environment variables |
| [Category reference](docs/categories/README.md) | Per-category help (Cat 034, 048, 062) — also in the UI |
| [Testing](backend/tests/README.md) | How to run unit, integration, live and regression tests |
| [Configurations](../configurations/README.md) | Save & share category setups via git |

## Features

- Create and edit ASTERIX messages via a browser UI
- Generate binary/hex output from field values
- Send messages over UDP or TCP
- Build and run scenarios with timing, repetition and loop control
- Save and load message templates and scenarios
