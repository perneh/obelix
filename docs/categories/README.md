# ASTERIX category reference

Obelix implements a subset of ASTERIX categories as encoders with matching UI forms. Each category has its own reference page:

| Category | Name | Edition | Help |
|----------|------|---------|------|
| **015** | INCS Target Reports | 1.1 (Part 28) | [cat015.md](cat015.md) |
| **016** | INCS Configuration Reports | 1.0 (Part 30) | [cat016.md](cat016.md) |
| **021** | ADS-B Target Reports | 2.7 (Part 12) | [cat021.md](cat021.md) |
| **034** | Monoradar Service Messages | 1.29 | [cat034.md](cat034.md) |
| **048** | Monoradar Target Reports | 1.32 | [cat048.md](cat048.md) |
| **062** | System Track Data | 1.21 (Eurocontrol Part 9) | [cat062.md](cat062.md) |

These files are served to the Obelix UI via `GET /api/categories/{category}/help` and can be read directly in the repository.

When adding a new category, create `docs/categories/catXXX.md` following the same structure and register the encoder in `backend/app/asterix/registry.py`.
