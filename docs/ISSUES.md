# Issues — Mikrotik Router HACS Integration

## Current Priorities

1. ISS-260320-options-flow-crash — Options flow crash on HA 2025.12+ (#470, #471)
2. ISS-260320-blocking-io — Blocking I/O in async methods
3. ISS-260320-sonarcloud-token — SonarCloud token expired

---

## Active

### ISS-260320-options-flow-crash — Options flow crash on HA 2025.12+
**Type:** Bug
**Priority:** Critical
**Created:** 2026-03-20
**Status:** 🟢 Active — fix in PR #19
**Source:** GitHub #470, #471

**Done:**
- ✅ Root cause identified: broken conditional `__init__` in `OptionsFlowWithConfigEntry` subclass
- ✅ Fix implemented: remove custom `__init__`, delegate to parent which stores as `_config_entry`

**Remaining:**
- Deploy to HA for validation
- Merge PR #19
- Create release v2.3.6
- Comment on upstream issues #470, #471

---

### ISS-260320-blocking-io — Blocking I/O in async methods
**Type:** Bug
**Priority:** High
**Created:** 2026-03-20
**Status:** 🟢 Active — fix in PR #19

**Done:**
- ✅ All `switch.py` async methods wrapped in `async_add_executor_job`
- ✅ `button.py` `async_press` wrapped
- ✅ `update.py` `async_install` wrapped (both RouterOS and RouterBOARD)
- ✅ `config_flow.py` `api.connect()` wrapped

**Remaining:**
- Deploy to HA for validation
- Merge PR #19

---

### ISS-260320-deadlock-run-script — Deadlock in mikrotikapi.py run_script
**Type:** Bug
**Priority:** Critical
**Created:** 2026-03-20
**Status:** 🟢 Active — fix in PR #19

**Done:**
- ✅ All manual `lock.acquire()`/`release()` replaced with `with self.lock:` context managers
- ✅ `run_script()` deadlock on missing script fixed

**Remaining:**
- Deploy to HA for validation
- Merge PR #19

---

### ISS-260320-sonarcloud-token — SonarCloud token expired
**Type:** Infrastructure
**Priority:** Medium
**Created:** 2026-03-20
**Status:** 🟢 Active

**Remaining:**
- Regenerate SONAR_TOKEN in GitHub repo secrets
- Verify SonarCloud analysis runs on next push

---

## Backlog

### ISS-260320-ruff-migration — Migrate from Black+flake8 to Ruff
**Type:** Quality
**Priority:** Low
**Created:** 2026-03-20
**Status:** 🟡 Backlog

**Remaining:**
- Replace Black + flake8 with Ruff in pre-commit and CI
- Add `pyproject.toml` with Ruff config
- Update CI workflow

---

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
