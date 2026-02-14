# Bugfix Documentation: OptionsFlow HA 2025.12+ Compatibility Fix

## Version: v2.2.1 (proposed)

**Base version:** v2.2 (upstream tomaae/homeassistant-mikrotik_router)
**Fork:** jnctech/homeassistant-mikrotik_router

---

## Problem Statement

Home Assistant 2025.12 introduced a breaking change to the `OptionsFlow` base class: `config_entry` became a **read-only property** managed by the framework. The Mikrotik Router integration was incompatible because it:

1. **Manually set `self._config_entry`** in the `MikrotikControllerOptionsFlowHandler.__init__()` constructor
2. **Imported the deprecated `CONN_CLASS_LOCAL_POLL`** constant (removed in recent HA versions)
3. **Used `self._config_entry`** instead of the framework-provided `self.config_entry` property

### Symptoms

- **500 Internal Server Error** when clicking "Configure" on the Mikrotik Router integration in HA 2025.12+
- `AttributeError` related to `config_entry` property conflicts
- Import errors from the removed `CONN_CLASS_LOCAL_POLL` constant

### Affected Users

All users running Home Assistant 2025.12 or later with Mikrotik Router integration installed via HACS.

---

## Fix Details

### Commit 1: `84706a2` — Core Fix (on master)

**"Fix 500 error on configure by updating OptionsFlow for HA 2025.12+"**

Changes to `custom_components/mikrotik_router/config_flow.py`:

| Change | Before | After |
|--------|--------|-------|
| Constructor | Custom `__init__` storing `self._config_entry` | Removed entirely |
| Base class import | `CONN_CLASS_LOCAL_POLL` imported | Removed deprecated import |
| Options flow factory | `MikrotikControllerOptionsFlowHandler(config_entry)` | `MikrotikControllerOptionsFlowHandler()` (no args) |
| Config entry access | `self._config_entry` (20+ references) | `self.config_entry` (framework property) |
| Options init | Done in constructor | Moved to `async_step_init()` |

### Commit 2: `25464c1` — Housekeeping (on master)

**"Add .gitignore to exclude __pycache__ directories"**

Added `.gitignore` with `__pycache__/` rule.

### Commit 3: `c54b209` — Refined Fix (on branch)

**"Add unit tests for config flow and use OptionsFlowWithConfigEntry"**

Refined the fix by switching from `OptionsFlow` to `OptionsFlowWithConfigEntry`:

| Change | Before (84706a2) | After (c54b209) |
|--------|-------------------|------------------|
| Base class | `OptionsFlow` | `OptionsFlowWithConfigEntry` |
| Constructor args | No args | `config_entry` passed to super |
| `self.options` init | Manual in `async_step_init` | Automatic (handled by base class) |

**Why `OptionsFlowWithConfigEntry` is better:**
- Available since HA 2024.3 (our minimum supported version)
- Explicitly manages `self.config_entry` and `self.options` across all HA versions
- Forward-compatible with future HA changes
- Recommended by HA development documentation

**Test suite added (352 lines):**

| Test | Coverage |
|------|----------|
| `test_flow_user_init` | Config flow form display |
| `test_flow_user_creates_entry` | Successful setup |
| `test_flow_user_connection_error` | Connection failure handling |
| `test_flow_user_wrong_login` | Auth failure handling |
| `test_flow_user_ssl_error` | SSL error handling |
| `test_flow_user_duplicate_name` | Duplicate name rejection |
| `test_flow_import` | Import source delegation |
| `test_options_flow_init` | Options form display |
| `test_options_flow_basic_to_sensor_select` | Step progression |
| `test_options_flow_complete` | Full options flow |
| `test_options_flow_preserves_existing_options` | Option defaults preserved |
| `test_options_flow_no_explicit_config_entry_set` | **Regression test for HA 2025.12+ fix** |

---

## Files Changed (cumulative from v2.2)

| File | Status | Purpose |
|------|--------|---------|
| `custom_components/mikrotik_router/config_flow.py` | Modified | Core bugfix |
| `custom_components/mikrotik_router/manifest.json` | Modified | Version bump |
| `.gitignore` | Added | Exclude __pycache__ |
| `custom_components/__init__.py` | Added | Package init for tests |
| `pytest.ini` | Added | Test configuration |
| `requirements_test.txt` | Added | Test dependencies |
| `tests/__init__.py` | Added | Test package init |
| `tests/conftest.py` | Added | Test fixtures |
| `tests/test_config_flow.py` | Added | Unit tests (352 lines) |

---

## Compatibility Matrix

| Home Assistant Version | Before Fix | After Fix |
|------------------------|-----------|-----------|
| < 2024.3.0 | Not supported (per hacs.json) | Not supported |
| 2024.3.0 - 2025.11.x | Working | Working |
| 2025.12+ | **500 Error on Configure** | Working |

---

## Testing Instructions

1. Install the fixed integration via HACS or manual copy
2. Navigate to Settings > Devices & Services > Mikrotik Router
3. Click "Configure" on an existing integration entry
4. Verify the options form loads without error
5. Submit changes and verify they are saved correctly

### Unit Tests

```bash
pip install -r requirements_test.txt
pytest tests/ -v
```
