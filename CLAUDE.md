# CLAUDE.md - Mikrotik Router HACS Integration

## Project

- **Domain:** `mikrotik_router` | **Version:** 2.3.5 | **IoT:** `local_polling` (30s)
- **HA Min:** 2024.3.0 | **Python:** 3.13 | **Fork of:** `tomaae/homeassistant-mikrotik_router`
- **Deps:** `librouteros>=3.4.1`, `mac-vendor-lookup>=0.1.12`
- **Platforms:** sensor, binary_sensor, switch, button, device_tracker, update

## AI Model Selection

| Context | Model | Co-author tag |
|---------|-------|---------------|
| Bug fixes, refactoring, tests | Sonnet | `Claude Sonnet 4.6` |
| Architecture, design | Opus | `Claude Opus 4.6 (1M context)` |

## Standards & References

- [HA Coding Standards](docs/ha-coding-standards.md) — async rules, entity patterns, datetime, type hints
- [Quality Gates](docs/quality-gates.md) — CI, SonarCloud, pre-commit, pre-PR checklist
- [Architecture Notes](docs/architecture.md) — coordinator design, API client, known caveats

## Git

- **Branches:** `master` (main), `dev`, `feature/<desc>`, `fix/<desc>`
- **Commits:** Conventional (`fix:`, `feat:`, `docs:`, `refactor:`, `chore:`)
- **PR target:** jnctech fork, never upstream unless explicitly told
