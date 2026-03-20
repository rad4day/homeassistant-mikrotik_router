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

(none yet)
