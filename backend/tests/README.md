# Obelix test suite

Functional, specification-style pytest tests for Obelix. Tests are plain functions composed from small support modules under `support/`.

> **Project mapping:** The prompt template uses a top-level `tests/` directory. In Obelix, tests live under `backend/tests/` with `pythonpath = ["backend"]` so imports resolve as `app.*` and `tests.support.*`.

## Quick start

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests (live tests skip automatically if no server is running)
pytest

# Or use the helper script
chmod +x scripts/test.sh
./scripts/test.sh          # all
./scripts/test.sh unit     # unit only
./scripts/test.sh integration  # in-process API tests
./scripts/test.sh live     # against running server
./scripts/test.sh cov      # with coverage
```

Run a single file:

```bash
pytest backend/tests/unit/test_encoding_cat034.py
```

Enable debug logging:

```bash
# Option A: environment variable
LOG_LEVEL=DEBUG pytest

# Option B: pytest built-in
pytest --log-cli-level=DEBUG
```

Run against a host (live integration tests):

```bash
./obelix start --dev   # in another terminal

pytest backend/tests/integration -m live --address=localhost --port=8000
pytest backend/tests/integration -m live --url=http://127.0.0.1:8000
TEST_URL=http://127.0.0.1:8000 pytest backend/tests/integration -m live
```

Verify custom CLI options:

```bash
pytest --help | grep -E 'address|port|url'
```

## Directory layout

```text
backend/tests/
├── conftest.py              # CLI options, session fixtures (target, api_client)
├── README.md                # this file
├── support/
│   ├── logging_config.py    # test-run logging setup
│   ├── cli_options.py       # --address, --port, --url resolution (pure)
│   ├── builders/            # pure payload and field builders
│   ├── actions/             # workflows (encode, HTTP calls)
│   └── assertions/          # reusable assertion helpers
├── unit/                    # pure encoding/registry tests
└── integration/             # API tests (in-process and live)
```

| Folder | Purpose |
|--------|---------|
| `unit/` | ASTERIX encoding and registry without network I/O |
| `integration/` | FastAPI endpoints via TestClient or live httpx client |
| `support/builders/` | Construct field values and API payloads (pure) |
| `support/actions/` | Execute workflows; log at DEBUG/INFO |
| `support/assertions/` | Compare actual vs expected with clear messages |

## Writing tests

Checklist:

1. Use a **plain function**, not a test class.
2. Name tests `test_<behavior>_when_<condition>`.
3. Keep test bodies **short** (wire builders → actions → assertions).
4. Put reusable logic in `support/`, not in test files.
5. Use `@pytest.mark.parametrize` for data-driven cases.
6. Mark tests: `@pytest.mark.unit`, `@pytest.mark.integration`, or `@pytest.mark.live`.

Example:

```python
@pytest.mark.unit
def test_north_marker_encodes_expected_hex():
    fields = build_cat034_north_marker_fields(sac=1, sic=2)
    result = run_encode_cat034_datablock(fields)
    assert_hex_equals(result, "220007C0010102")
```

Use **parametrize** when the workflow is identical and only inputs differ. Add a new test function when behavior or assertions differ meaningfully.

## Support library

| Layer | Module | Import example |
|-------|--------|----------------|
| Builders | `tests.support.builders.encoding` | `build_cat034_north_marker_fields()` |
| Actions | `tests.support.actions.http` | `run_list_categories(client)` |
| Assertions | `tests.support.assertions.http` | `assert_status_ok(result)` |

Import symbols explicitly — no star imports.

## Logging

- Configured in `tests/support/logging_config.py`, invoked from `conftest.py`.
- Default level: **WARNING**.
- Set `LOG_LEVEL=DEBUG` or `pytest --log-cli-level=DEBUG` for verbose output.
- Actions log workflow steps at DEBUG; milestones at INFO; failures at ERROR with context.
- **Do not** use `print()` in tests or support code.

## CLI options

Registered in `conftest.py`, resolved in `tests/support/cli_options.py`.

| Option | Purpose | Example |
|--------|---------|---------|
| `--address` | Host under test | `--address=192.168.1.10` |
| `--port` | TCP port | `--port=8080` |
| `--url` | Full base URL (overrides address/port) | `--url=http://staging:9000` |

**Precedence:** `--url` → `TEST_URL` → `--address` + `--port` → `TEST_ADDRESS` / `TEST_PORT` → defaults (`127.0.0.1:8000`).

Session fixture `target` exposes a frozen `TargetConfig` dataclass. Tests and support code receive it as an argument — **do not** read `pytestconfig` inside test files.

Live tests use the `live_http_client` fixture, which skips gracefully when the server is unreachable.

## Markers

| Marker | Meaning |
|--------|---------|
| `unit` | No external I/O |
| `integration` | API boundary tests |
| `live` | Requires running server (auto-skip if down) |
| `slow` | Reserved for long-running tests |

```bash
pytest -m unit
pytest -m "integration and not live"
pytest -m live --url=http://localhost:8000
```

## CI

Example pipeline command (unit + in-process integration, no live server required):

```bash
pip install -e ".[dev]"
pytest -m "unit or (integration and not live)" --cov=app --cov-report=xml
```

For live smoke tests in CI when a server is deployed:

```bash
TEST_URL=https://obelix.example.com pytest -m live
```

## Anti-patterns

- Test classes (use functions + parametrize)
- Business logic duplicated across test files
- `print()` for diagnostics
- Shared mutable globals between tests
- `time.sleep()` without timeout/polling strategy
- Reading `request.config` or `pytestconfig` directly in tests — use fixtures instead

## Adding a new test

1. Add a **builder** in `support/builders/` if new test data is needed.
2. Add an **action** in `support/actions/` if a new workflow is reused.
3. Add an **assertion** in `support/assertions/` for reusable checks.
4. Write a short test function in `unit/` or `integration/` that composes them.
5. Run `pytest` and `./scripts/test.sh unit` (or `integration`) as appropriate.
