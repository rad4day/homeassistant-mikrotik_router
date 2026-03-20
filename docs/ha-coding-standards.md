# HA Coding Standards

Non-negotiable rules for this integration. Violations are bugs.

## Async / Blocking I/O

NEVER call blocking I/O from `async_` methods. Wrap with executor:

```python
# WRONG — blocks event loop
async def async_turn_on(self):
    self.coordinator.set_value(...)

# CORRECT
async def async_turn_on(self):
    await self.hass.async_add_executor_job(self.coordinator.set_value, ...)
    await self.coordinator.async_refresh()
```

Applies to: `switch.py`, `button.py`, `update.py`, `config_flow.py` — any `async_` method calling `MikrotikAPI` or coordinator network methods.

## Lock Management

Always use context managers. Manual `acquire()`/`release()` deadlocks on early return or exception.

```python
# WRONG                          # CORRECT
self.lock.acquire()              with self.lock:
# ...                               # ...
self.lock.release()
```

## OptionsFlow

Use `OptionsFlowWithConfigEntry` with NO custom `__init__`. HA 2025.12+ auto-injects `config_entry`.

## DeviceInfo

Use `name=`, `manufacturer=`, `model=`. The `default_name`, `default_manufacturer`, `default_model` params are deprecated and will be removed.

## Datetime

Use HA utilities, never naive datetimes:

```python
from homeassistant.util.dt import now as dt_now, utc_from_timestamp
# NOT: datetime.now(), datetime.utcfromtimestamp()
```

## Type Hints

- `from __future__ import annotations` in every file
- PEP 604: `str | None` not `Optional[str]`
- Built-in generics: `list`, `dict` not `List`, `Dict`
- All public methods need return type hints
- Import `Optional` from `typing`, never `voluptuous`

## Translations

- `strings.json` is source of truth — `translations/` inherits from it
- Every config option in the UI must have a `strings.json` entry
- Keep `strings.json` and `translations/en.json` in sync
