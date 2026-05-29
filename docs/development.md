# Development

## Development

See [backend/tests/README.md](backend/tests/README.md) for the full testing guide (functional pytest layout, logging, CLI options).

### Running tests

```bash
pip install -e ".[dev]"
pytest                              # all tests
./scripts/test.sh unit              # unit only
./scripts/test.sh integration       # in-process API tests
./scripts/test.sh live -- --url=http://127.0.0.1:8000  # live server
LOG_LEVEL=DEBUG pytest --log-cli-level=DEBUG
```

## Adding a new ASTERIX category

Cat 062 follows the same plugin pattern. See `backend/app/asterix/categories/cat062.py` for a full Eurocontrol Part 9 ed. 1.21 example with UAP FRN mappings.

1. Create `backend/app/asterix/categories/catXXX.py` implementing `AsterixCategory`.
2. Define fields in `definition()` with correct UAP FRN mappings.
3. Implement `encode_record()` using `build_fspec()` and item encoders.
4. Register the class in `backend/app/asterix/registry.py`.
5. Add encoding tests in `backend/tests/unit/` using the support library — see [backend/tests/README.md](../backend/tests/README.md).
6. Add a category reference page in `docs/categories/catXXX.md` (served to the UI via `GET /api/categories/{category}/help`).

The frontend will automatically pick up the new category via the API.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OBELIX_SHARED_CONFIGURATIONS_DIR` | `configurations` | Git-tracked presets (`scope=shared`) |
| `OBELIX_LOCAL_CONFIGURATIONS_DIR` | `data/configurations` | Local saves (`scope=local`) |
| `OBELIX_SCENARIOS_DIR` | `data/scenarios` | Saved scenarios |
| `OBELIX_HOST` | `0.0.0.0` | Server bind host |
| `OBELIX_PORT` | `8000` | Server bind port |
