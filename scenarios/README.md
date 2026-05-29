# Scenario library

Pre-built realistic ASTERIX exercise scenarios for Obelix.

| File | Description |
|------|-------------|
| `shared/jas-bromma-visby.json` | JAS 39 Gripen Bromma → Visby (all categories) |
| `shared/mig-kaliningrad-visby.json` | Hostile MiG Kaliningrad → Visby |
| `shared/baltic-combined.json` | Combined Baltic exercise (JAS + MiG) |

Each scenario includes steps for **all implemented categories** (015, 016, 021, 034, 048, 062, 065, and 240). Categories **015, 021, 034, 048, 062, and 240** use route animation; **016** and **065** are sent with repeat (no motion).

Custom scenarios saved from the UI go to `data/scenarios/` (local). Copy JSON into `scenarios/shared/` and commit when you want a variant in git.

Regenerate shared JSON from Python templates:

```bash
python3 -c "
from pathlib import Path
from app.scenarios.templates import build_template
out = Path('scenarios/shared')
for tid in ['jas-bromma-visby', 'mig-kaliningrad-visby', 'baltic-combined']:
    (out / f'{tid}.json').write_text(build_template(tid).model_dump_json(indent=2))
"
```
