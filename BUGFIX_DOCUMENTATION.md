# Bugfix Documentation: OptionsFlow HA 2025.12+ Compatibility Fix

## Version: v2.2.2 (current fork)

**Base version:** v2.2 (upstream tomaae/homeassistant-mikrotik_router)
**Fork:** jnctech/homeassistant-mikrotik_router
**Upstream PR:** tomaae/homeassistant-mikrotik_router#464 (open, awaiting review)

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

## Fix History

### Iteration 1: `84706a2` — Initial Fix

**"Fix 500 error on configure by updating OptionsFlow for HA 2025.12+"**

Switched from broken manual `__init__` pattern to plain `OptionsFlow`. Removed deprecated `CONN_CLASS_LOCAL_POLL`. Options initialised manually in `async_step_init`.

### Iteration 2: `c54b209` — Switch to OptionsFlowWithConfigEntry (SUPERSEDED)

Switched to `OptionsFlowWithConfigEntry` for automatic `self.options` management. Added unit test suite. This was later found to be using a deprecated class.

> **Note:** `OptionsFlowWithConfigEntry` is explicitly deprecated in HA core (phased out for core/built-in integrations; kept only for custom integration backward compatibility). `custom_integration_behavior=ReportBehavior.IGNORE` means it produces no warnings at runtime for custom integrations, but it is not the recommended pattern.

### Iteration 3: `14131fc` / `57ce6db` — Final Fix (current) ✓

**"Use plain OptionsFlow instead of deprecated OptionsFlowWithConfigEntry"**

This is the correct, recommended pattern per HA core documentation.

| Change | Upstream (broken) | Iteration 2 | **Current (correct)** |
|--------|-------------------|-------------|----------------------|
| Base class | `OptionsFlow` (misused) | `OptionsFlowWithConfigEntry` (deprecated) | **`OptionsFlow`** |
| `__init__` | Manually set `self._config_entry` | Removed (base handled it) | **No `__init__` at all** |
| Handler factory arg | `config_entry` passed | `config_entry` passed | **No args** |
| Options dict | `self._config_entry.options.get(...)` | `self.options` (deepcopy from base) | **`self._options`** (init'd in `async_step_init`) |

**Why plain `OptionsFlow` is correct:**
- `OptionsFlowWithConfigEntry` docstring: *"This class is being phased out, and should not be referenced in new code."*
- `self.config_entry` is injected by the framework as a property after construction — no need to pass it manually
- `self.config_entry` is **not** available in `__init__`; it becomes available from `async_step_init` onward
- `self._options` is initialised in `async_step_init` as `dict(self.config_entry.options)` — a mutable working copy accumulated across the two-step form

**Test suite (12 tests):**

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
| `test_options_flow_complete` | Full two-step options flow |
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

Tests require `pytest-homeassistant-custom-component`. Run in the docker-dev environment:

```bash
# SSH into docker-dev
ssh jc@192.168.30.10 -p 2222

# Navigate to repo
cd /workspace/hacs/Mikrotik   # or wherever the repo is mounted

# Install deps (first time only)
pip install -r requirements_test.txt

# Run tests
pytest tests/ -v
```

Expected output: all 12 tests pass.

> **Important:** Tests were **not** run before pushing to the upstream PR. They should be run in docker-dev to validate the current fix before any further upstream engagement.
