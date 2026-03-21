# Change Register — Mikrotik Router HACS Integration

Changes listed in reverse chronological order.

---

## CR-260321-complexity-reduction — Cognitive complexity reduction across coordinator, entity, apiparser

**Date:** 2026-03-21
**Branch:** `feature/complexity-reduction`
**PR:** #30 (targeting dev)
**Status:** In Review

### What Changed

| Area | Change |
|------|--------|
| `coordinator.py` | Extracted 11 helpers from `async_process_host()` (136→~10 each): `_merge_capsman_hosts`, `_merge_wireless_hosts`, `_merge_dhcp_hosts`, `_merge_arp_hosts`, `_recover_hass_hosts`, `_ensure_host_defaults`, `_update_host_availability`, `_update_host_address`, `_resolve_hostname`, `_dhcp_comment_for_host`, `_update_captive_portal` |
| `coordinator.py` | Extracted `_async_update_hwinfo` and `_async_run_if_connected` from `_async_update_data()` (65→~15), plus optional sensor loop tables |
| `coordinator.py` | Extracted `_init_accounting_hosts`, `_classify_accounting_traffic`, `_check_accounting_threshold`, `_apply_accounting_throughput` from `process_accounting()` (48→~10 each) |
| `coordinator.py` | Extracted `_monitor_ethernet_port` with SFP/copper/PoE monitor val constants from `get_interface()` (27→~10) |
| `entity.py` | Split `_skip_sensor()` into `_skip_interface_traffic`, `_skip_binary_sensor`, `_skip_device_tracker`, `_skip_poe_sensor` (23→~5 each) |
| `switch.py` | Replaced inline attribute loops with shared `copy_attrs` from entity.py (21→~5) |
| `apiparser.py` | Extracted `_traverse_entry` helper with `_NOT_FOUND` sentinel, case-insensitive bool matching via frozensets (18→~8) |
| `coordinator.py` | Further extracted `_hostname_from_dns`, `_hostname_from_dhcp`, `_add_traffic_bytes` to bring two remaining functions under threshold |
| `coordinator.py` | Silent-failure fixes: username guard in `get_access`, debug logging on MAC lookup, ValueError guard on `_address_part_of_local_network` |
| `coordinator.py` | Restored independent `connected()` check between `get_wireless`/`get_wireless_hosts`; guarded `_apply_accounting_throughput` against zero `time_diff` |
| `tests/` | 58 new tests covering all extracted helpers (361 total, up from 303) |
| `docs/decisions/` | ADR-007: Cognitive Complexity Reduction via Helper Extraction |
| `docs/ISSUES.md` | Added ISS-260321-silent-failures tracking remaining audit findings |

### Why

ISS-260321-cognitive-complexity: SonarCloud quality target is ≤15 cognitive complexity per function. Seven of the worst offenders (totalling 358 complexity points) are now refactored into focused helpers, each well under the threshold. Silent-failure audit (pr-review-toolkit) identified 12 issues; 3 critical/high fixed, 8 pre-existing tracked.

### Quality Gate Results

| Metric | Value | Gate |
|--------|-------|------|
| Ruff lint | 0 errors | ✅ |
| Ruff format | 0 reformats needed | ✅ |
| Tests | 361 passed, 5 skipped | ✅ |

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
