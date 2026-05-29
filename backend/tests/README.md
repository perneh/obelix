# Obelix test suite

Functional, specification-style pytest tests for Obelix. Tests are plain functions composed from small support modules under `support/`.

> **Project mapping:** The prompt template uses a top-level `tests/` directory. In Obelix, tests live under `backend/tests/` with `pythonpath = ["backend"]` so imports resolve as `app.*` and `tests.support.*`.

## Quick start

Install dev dependencies once:

```bash
pip install -e ".[dev]"
chmod +x scripts/test.sh
```

Start Obelix when running **live** or **regression** tests (in another terminal):

```bash
./obelix start --dev
```

## Running tests

All commands assume you are in the **repository root**.

| What | Command |
|------|---------|
| **All tests** | `./scripts/test.sh` or `pytest` |
| **Unit** (encoding, registry — no I/O) | `./scripts/test.sh unit` |
| **Integration** (in-process API, TestClient) | `./scripts/test.sh integration` |
| **Live integration** (running server) | `./scripts/test.sh live --address=localhost --port=8000` |
| **Regression** (HTTP API, per endpoint) | `./scripts/test.sh regression --address=localhost --port=8000` |
| **Coverage** | `./scripts/test.sh cov` |

Equivalent `pytest` invocations:

```bash
pytest                                          # all
pytest backend/tests/unit -m unit               # unit
pytest backend/tests/integration -m "integration and not live"   # integration
pytest backend/tests/integration -m live --address=localhost --port=8000
pytest backend/tests/regression -m regression --address=localhost --port=8000
```

### Stop on first failure and show statistics

Add these flags to any command above:

| Flag | Effect |
|------|--------|
| `-x` / `--exitfirst` | Stop as soon as one test fails |
| `-v` | Print each test name and PASSED/FAILED while running |
| `-rA` | Extra summary at the end (passed, failed, skipped, …) |
| `--tb=short` | Shorter traceback on failures |

**Regression example** (server must be running):

```bash
./scripts/test.sh regression --address=localhost --port=8000 -x -v -rA --tb=short
```

**Unit example:**

```bash
./scripts/test.sh unit -x -v
```

Pytest always prints a final line such as `5 passed in 0.45s` or `1 failed, 4 passed in 1.2s`.

### Single file or single test

```bash
pytest backend/tests/unit/test_encoding_cat034.py
pytest backend/tests/regression/test_cat015.py -v
pytest backend/tests/regression/test_send.py::test_send -x -v
```

### Remote host (regression / live)

```bash
pytest backend/tests/regression -m regression --address=192.168.1.10 --port=8000 -x -v

# Or via environment
TEST_ADDRESS=10.0.0.5 TEST_PORT=8080 pytest backend/tests/regression -m regression
TEST_URL=http://staging.example.com pytest backend/tests/regression -m regression
```

Default target when `--address` / `--port` are omitted: `localhost:8000`.

### Debug logging

```bash
LOG_LEVEL=DEBUG pytest backend/tests/regression -m regression -v
pytest --log-cli-level=DEBUG backend/tests/regression -m regression
```

Verify custom CLI options:

```bash
pytest --help | grep -E 'address|port|url'
```

Regression layout:

| Suite | File | Endpoints covered |
|-------|------|-------------------|
| Health | `regression/test_health.py` | `GET /api/categories` |
| Frontend | `regression/test_frontend.py` | `GET /` |
| Cat 015–240 | `regression/test_cat*.py` | category detail, help, `POST /api/encode` |
| Configurations | `regression/test_configurations.py` | `/api/configurations` CRUD |
| Scenarios | `regression/test_scenarios.py` | validate, motion-defaults, runs |
| Templates | `regression/test_scenario_templates.py` | `/api/scenario-templates` |
| Saved scenarios | `regression/test_saved_scenarios.py` | `/api/saved-scenarios` |
| Send | `regression/test_send.py` | `POST /api/encode`, `POST /api/send` |

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
│   │   ├── http.py          # integration tests (TestClient / live client)
│   │   └── regression_http.py  # regression: get/post/delete(address, port, path)
│   └── assertions/          # reusable assertion helpers
├── unit/                    # pure encoding/registry tests
├── integration/             # API tests (in-process and live)
└── regression/              # live HTTP regression suites (httpx, per category)
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
| Regression HTTP | `tests.support.actions.regression_http` | `get(address, port, "/api/categories")` |
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

**Precedence:** `--url` → `TEST_URL` → `--address` + `--port` → `TEST_ADDRESS` / `TEST_PORT` → defaults (`localhost:8000`).

Session fixtures `address` and `port` (regression) or `live_http_client` (live integration) skip gracefully when the server is unreachable.

## Markers

| Marker | Meaning |
|--------|---------|
| `unit` | No external I/O |
| `integration` | API boundary tests |
| `live` | Requires running server (auto-skip if down) |
| `regression` | Live HTTP regression against running backend (auto-skip if down) |
| `slow` | Reserved for long-running tests |

```bash
pytest -m unit
pytest -m "integration and not live"
pytest -m live --url=http://localhost:8000
pytest -m regression --address=localhost --port=8000
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
