# Change Register — Mikrotik Router HACS Integration

Changes listed in reverse chronological order.

---

## CR-260320-tests-and-refactor — Test suite, devcontainer, CI/CD alignment, ruff migration

**Date:** 2026-03-20
**Branch:** `feature/tests-and-refactor`
**PR:** [#29](https://github.com/jnctech/homeassistant-mikrotik_router/pull/29)
**Status:** In Review (targeting dev)

### What Changed

| Area | Change |
|------|--------|
| `tests/` | 151+ tests across 7 files: apiparser (52), mikrotikapi (30), helper (13), coordinator (80), entity (30), update (8) |
| `.devcontainer/` | Python 3.13 devcontainer with pytest-homeassistant-custom-component, Ruff, Pylance |
| `.github/workflows/` | CI/CD aligned to gold standard: SHA-pinned actions, Ruff replaces Black+flake8, gitleaks, pip-audit, actionlint, dependency-review, scorecard added |
| `.github/dependabot.yml` | Dependabot configured for GitHub Actions and pip |
| `requirements_dev.txt` | New: all dev/test dependencies |
| `requirements_tests.txt` | Modernised from 2019-era pinned versions to match CI |
| `apiparser.py` | `type() == dict` → `isinstance(source, dict)` (E721) |
| `*.py` (14 files) | Ruff: remove 43 unused imports (F401), reformat 4 files |
| `docs/quality-gates.md` | Black/flake8 → Ruff references, local dev setup instructions |
| `docs/ISSUES.md` | Test coverage plan, refactor backlog, status updates |

### Why

1. Test coverage was ~11% — well below the 80% SonarCloud target
2. No local dev environment — tests could only run in CI
3. CI was using unpinned actions and legacy linters (Black+flake8)
4. Ruff migration tracked as ISS-260320-ruff-migration — now completed

### Quality Gate Results

| Metric | Value | Gate |
|--------|-------|------|
| Ruff lint | 0 errors | ✅ |
| Ruff format | 0 reformats needed | ✅ |
| Tests | 151+ (CI pending) | ⏳ |

### Post-Deploy Actions

- [ ] Open in devcontainer and verify `pytest tests/ -v` passes
- [ ] Confirm CI passes on dev branch
- [ ] Measure coverage and compare against 80% target

---

## CR-260320-dispatcher-spam — Disable update_sensors dispatcher to fix log spam

**Date:** 2026-03-20
**Branch:** `fix/disable-dispatcher-spam-v2`
**PR:** [#26](https://github.com/jnctech/homeassistant-mikrotik_router/pull/26)
**Status:** Merged (v2.3.8)

### What Changed

| Area | Change |
|------|--------|
| `coordinator.py` | Disable `async_dispatcher_send("update_sensors")` that caused "does not generate unique IDs" log errors every 30s |

### Why

The dispatcher re-enabled in v2.3.6 for new device discovery caused thousands of log errors because `_check_entity_exists()` doesn't guard against re-adding existing entities. Proper fix tracked as ISS-260320-new-device-discovery.

---

## CR-260320-arp-failed-filter — ARP failed-status filtering for device tracking

**Date:** 2026-03-20
**Branch:** `fix/arp-failed-filter-v2`
**PR:** [#23](https://github.com/jnctech/homeassistant-mikrotik_router/pull/23)
**Status:** Merged (v2.3.7)

### What Changed

| Area | Change |
|------|--------|
| `coordinator.py` | Move ARP failed-status filtering from `get_arp()` to `async_process_host()` |

### Why

ARP entries with `status: failed` were causing devices to show as home when they were unreachable. Failed entries are now excluded from `arp_detected` but kept in `ds["arp"]` for bridge-interface lookups. Fixes [#17](https://github.com/jnctech/homeassistant-mikrotik_router/issues/17).

---

## CR-260320-ha-compliance-blocking-io — HA compliance: deadlocks, blocking I/O, options flow crash

**Date:** 2026-03-20
**Branch:** `fix/ha-compliance-blocking-io-deadlocks`
**PR:** [#19](https://github.com/jnctech/homeassistant-mikrotik_router/pull/19)
**Status:** Merged (v2.3.6)

### What Changed

| Area | Change |
|------|--------|
| `mikrotikapi.py` | Replace all manual `lock.acquire()`/`release()` with `with self.lock:` context managers — fixes critical deadlock in `run_script()` |
| `mikrotikapi.py` | Fix wrong `voluptuous.Optional` import → `list \| None`; fix return type `(bool, bool)` → `tuple[bool, bool]` |
| `config_flow.py` | Remove broken `__init__` from `OptionsFlowWithConfigEntry` subclass — fixes #470, #471 |
| `config_flow.py` | Wrap blocking `api.connect()` in `async_add_executor_job` |
| `switch.py` | Wrap all blocking `set_value`/`execute` calls in `async_add_executor_job` |
| `switch.py` | Remove dead sync `turn_on`/`turn_off` stubs |
| `button.py` | Wrap blocking `run_script` in `async_add_executor_job` |
| `update.py` | Wrap blocking `execute` calls in `async_add_executor_job` (RouterOS + RouterBOARD) |
| `entity.py` | Replace deprecated `default_name`/`default_manufacturer`/`default_model` with `name`/`manufacturer`/`model` |
| `strings.json` | Add missing `sensor_poe` translation entry |
| `CLAUDE.md` | New project CLAUDE.md with quality targets and linked standards |
| `docs/` | New: `ha-coding-standards.md`, `quality-gates.md`, `architecture.md`, `ISSUES.md`, `CHANGE-REGISTER.md` |

### Why

Multiple HA best-practice violations discovered during HACS compliance audit:
1. Options flow crash reported by users on HA 2025.12+ (GitHub #470, #471)
2. Blocking network I/O on the event loop freezing HA UI
3. Critical deadlock bug in `run_script()` that permanently freezes the integration
4. Deprecated APIs that will be removed in future HA releases

### Post-Deploy Actions

- [x] Validate options flow opens without error on HA
- [x] Toggle a switch and verify no UI freeze
- [x] Run a script button and verify no deadlock
- [ ] Comment on upstream issues #470, #471
