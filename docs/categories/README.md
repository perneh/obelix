# ASTERIX category reference

Obelix implements a subset of ASTERIX categories as encoders with matching UI forms. Each category has its own reference page:

| Category | Name | Edition | Help |
|----------|------|---------|------|
| **034** | Monoradar Service Messages | 1.29 | [cat034.md](cat034.md) |
| **048** | Monoradar Target Reports | 1.32 | [cat048.md](cat048.md) |
| **062** | System Track Data | 1.21 (Eurocontrol Part 9) | [cat062.md](cat062.md) |

These files are served to the Obelix UI via `GET /api/categories/{category}/help` and can be read directly in the repository.

When adding a new category, create `docs/categories/catXXX.md` following the same structure and register the encoder in `backend/app/asterix/registry.py`.
