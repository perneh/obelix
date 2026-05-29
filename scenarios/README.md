# Scenario library

Pre-built realistic ASTERIX exercise scenarios for Obelix.

| File | Description |
|------|-------------|
| `shared/jas-bromma-visby.json` | JAS 39 Gripen Bromma → Visby (all categories) |
| `shared/mig-kaliningrad-visby.json` | Hostile MiG Kaliningrad → Visby |
| `shared/baltic-combined.json` | Combined Baltic exercise (JAS + MiG) |

Each scenario uses **categories 015, 016, 021, 034, 048, and 062** with motion along geographic routes.

Custom scenarios saved from the UI go to `data/scenarios/` (local). Use **Save to repository** to store variants under `scenarios/shared/`.

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
