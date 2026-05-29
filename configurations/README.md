# ASTERIX message configurations

Saved field values for each ASTERIX category. Use these files to version-control message setups and share them via git.

## Layout

```text
configurations/
├── cat015/          # INCS target reports
├── cat016/          # INCS configuration reports
├── cat021/          # ADS-B target reports
├── cat034/          # Monoradar service messages
├── cat048/          # Monoradar target reports
├── cat062/          # System track data
├── cat065/          # SDPS service status reports
├── cat240/          # Radar video transmission
└── README.md

data/configurations/ # Local-only saves (not tracked by git)
└── catXXX/
    └── my-config.json
```

Each file is JSON with:

| Field | Description |
|-------|-------------|
| `id` | Filename slug (e.g. `system-track-wgs84`) |
| `name` | Display name in the UI |
| `description` | Optional notes |
| `scope` | `shared` (this folder) or `local` (`data/configurations/`) |
| `message.category` | ASTERIX category number |
| `message.fields` | Field values for encoding |

## Save from the UI

| Button | Scope | Location |
|--------|-------|----------|
| **Save locally** | `local` | `data/configurations/catXXX/` |

Load configurations from the **Configurations** tab (grouped by category).

To share a preset via git, copy or move the JSON into the matching `configurations/catXXX/` folder and commit (see below).

## Push to git

When a configuration is ready to share with the team:

```bash
# Example: commit a new Cat 062 setup
git add configurations/cat062/system-track-wgs84.json
git commit -m "Add Cat 062 system track preset for Stockholm test case"
git push
```

Shared presets exist for all implemented categories: **015, 016, 021, 034, 048, 062, 065, and 240**.

Local-only configs under `data/configurations/` are gitignored and stay on your machine.

## API

```bash
# List all configurations
curl http://localhost:8000/api/configurations

# Filter by category
curl http://localhost:8000/api/configurations?category=62

# Filter shared presets only
curl http://localhost:8000/api/configurations?scope=shared

# Load one
curl http://localhost:8000/api/configurations/shared:cat062:system-track-wgs84
```
