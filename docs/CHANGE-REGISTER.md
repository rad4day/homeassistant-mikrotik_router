# Change Register — Mikrotik Router HACS Integration

Changes listed in reverse chronological order.

---

## CR-260320-ha-compliance-blocking-io — HA compliance: deadlocks, blocking I/O, options flow crash

**Date:** 2026-03-20
**Branch:** `fix/ha-compliance-blocking-io-deadlocks`
**PR:** [#19](https://github.com/jnctech/homeassistant-mikrotik_router/pull/19)
**Status:** In Review

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

### Quality Gate Results

| Metric | Value | Gate |
|--------|-------|------|
| Tests | 59 passed, 5 skipped | ✅ |
| Black format | Clean | ✅ |
| Bandit | Clean | ✅ |
| hassfest | Pass | ✅ |
| HACS validation | Pass | ✅ |
| SonarCloud | Token expired (infra issue) | ⚠️ |

### Post-Deploy Actions

- [ ] Validate options flow opens without error on HA
- [ ] Toggle a switch and verify no UI freeze
- [ ] Run a script button and verify no deadlock
- [ ] Comment on upstream issues #470, #471
