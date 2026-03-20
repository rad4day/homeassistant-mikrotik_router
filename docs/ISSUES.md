# Issues — Mikrotik Router HACS Integration

## Current Priorities

1. ISS-260320-test-coverage — Increase test coverage to ≥80%
2. ISS-260320-new-device-discovery — New devices require HA restart to appear
3. ISS-260320-deprecated-datetime — Remaining naive datetime.now() calls

---

## Active

### ISS-260320-test-coverage — Increase test coverage to ≥80%
**Type:** Testing
**Priority:** High
**Created:** 2026-03-20
**Status:** 🟢 Active — PR #29 (feature/tests-and-refactor → dev)

**Done:**
- ✅ Phase 1: `helper.py` (13 tests), `apiparser.py` (52 tests), `mikrotikapi.py` (30 tests), `coordinator.py` basics (12 tests)
- ✅ Phase 2: coordinator data methods — get_system_resource, get_firmware_update, get_nat/mangle/filter, get_interface, get_dhcp, get_access (38 tests)
- ✅ Phase 3: entity helpers — _skip_sensor, _copy_attrs, MikrotikInterfaceEntityMixin (10 new tests), update.py pure functions (8 tests)
- ✅ Devcontainer setup for local testing with pytest-homeassistant-custom-component
- ✅ Ruff migration: all 32 source files pass lint and format

**Remaining:**
- Phase 4: integration lifecycle tests (async_setup_entry, async_migrate_entry) — needs devcontainer
- Platform entity integration tests (async_turn_on, is_connected, native_value) — needs devcontainer
- process_accounting — client traffic snapshot processing
- Full coverage measurement and gap analysis

**Reference:** 151+ tests written, target ≥80% for SonarCloud Grade A

---

## Backlog

### ISS-260320-new-device-discovery — New devices require HA restart to appear
**Type:** Feature
**Priority:** High
**Created:** 2026-03-20
**Status:** 🟡 Backlog
**Source:** coordinator.py line 692, entity.py lines 154-168

**Context:**
The `update_sensors` dispatcher was re-enabled in v2.3.6 to fix new devices not appearing, but it caused thousands of "does not generate unique IDs" log errors every 30s because `_check_entity_exists()` doesn't guard against re-adding existing entities. Reverted in v2.3.8.

**Remaining:**
- Track previously seen UIDs per data path in the coordinator (e.g. `self._known_uids["host"]`)
- Only fire `async_dispatcher_send("update_sensors", self)` when new UIDs appear that weren't in the previous set
- Alternatively, fix `_check_entity_exists()` to skip entities already in `platform.entities`
- Test: add a new host to `ds["host"]` mid-run and verify entity is created without log errors

---

### ISS-260320-deprecated-datetime — Remaining naive datetime.now() calls
**Type:** Bug
**Priority:** Medium
**Created:** 2026-03-20
**Status:** 🟡 Backlog
**Source:** coordinator.py lines 577, 606, 1547

**Remaining:**
- Replace `datetime.now()` with `homeassistant.util.dt.now()`
- Audit all datetime usage in coordinator.py

---

### ISS-260320-refactor-dedup — Refactor duplicated patterns
**Type:** Refactoring
**Priority:** Medium
**Created:** 2026-03-20
**Status:** 🟡 Backlog

**Remaining:**
- coordinator.py: extract firewall rule dedup helper (get_nat/get_mangle/get_filter share ~75 LOC pattern)
- switch.py: extract base class for NAT/Mangle/Filter/Queue UID lookup (~50 LOC)
- apiparser.py: extract shared path traversal from from_entry/from_entry_bool (~20 LOC)
- *_types.py: extract shared entity description base class (~80 LOC)

**Reference:** SonarCloud CPD exclusions already cover sensor_types.py and coordinator.py intentional repetition

---

## Completed

### ISS-260320-options-flow-crash — Options flow crash on HA 2025.12+
**Type:** Bug | **Priority:** Critical | **Created:** 2026-03-20
**Status:** 🔴 Closed — fixed in v2.3.6 (PR #19)

### ISS-260320-blocking-io — Blocking I/O in async methods
**Type:** Bug | **Priority:** High | **Created:** 2026-03-20
**Status:** 🔴 Closed — fixed in v2.3.6 (PR #19)

### ISS-260320-deadlock-run-script — Deadlock in mikrotikapi.py run_script
**Type:** Bug | **Priority:** Critical | **Created:** 2026-03-20
**Status:** 🔴 Closed — fixed in v2.3.6 (PR #19)

### ISS-260320-sonarcloud-token — SonarCloud token expired
**Type:** Infrastructure | **Priority:** Medium | **Created:** 2026-03-20
**Status:** 🔴 Closed — burner token set, SonarCloud passing

### ISS-260320-dispatcher-spam — Duplicate entity log errors from update_sensors
**Type:** Bug | **Priority:** High | **Created:** 2026-03-20
**Status:** 🔴 Closed — dispatcher disabled in v2.3.8 (PR #26). Proper fix tracked as ISS-260320-new-device-discovery

### ISS-260320-ruff-migration — Migrate from Black+flake8 to Ruff
**Type:** Quality | **Priority:** Low | **Created:** 2026-03-20
**Status:** 🔴 Closed — completed in PR #29 (feature/tests-and-refactor). CI uses ruff, all files formatted.
