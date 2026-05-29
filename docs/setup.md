# Setup

## Requirements

- Python 3.11+
- pip or uv
- Docker and Docker Compose v2 (optional, recommended)
- Wireshark 3.x+ (optional, for ASTERIX packet inspection — see [Wireshark & ASTERIX](wireshark-asterix.md))

## With Docker (recommended)

```bash
chmod +x obelix

./obelix start              # Production mode (built image)
./obelix start --dev        # Dev mode: mounted code + hot reload
./obelix start --dev --tools  # Dev + UDP test receiver on port 8600
./obelix stop
./obelix logs -f app
./obelix status
```

Open [http://localhost:8000](http://localhost:8000).

| Command | Description |
|---------|-------------|
| `./obelix start` | Start app in production mode |
| `./obelix start --dev` | Mount `backend/`, `frontend/`, `data/` with uvicorn `--reload` |
| `./obelix start --tools` | Also start UDP receiver on port 8600 |
| `./obelix stop` | Stop all services |
| `./obelix restart --dev` | Restart in dev mode |
| `./obelix logs -f` | Follow app logs |
| `./obelix shell` | Shell into the app container |

### Docker environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OBELIX_HTTP_PORT` | `8000` | Host port for the web UI |
| `OBELIX_UDP_PORT` | `8600` | Host port for the UDP test receiver |

## Without Docker

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run the server
uvicorn app.main:app --reload --app-dir backend
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).
