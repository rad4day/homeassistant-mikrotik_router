# ADR-006: Replace naive datetime.now() with HA utility

**Date:** 2026-03-21
**Status:** Proposed

## Context

Home Assistant deprecated naive `datetime.now()` calls in integrations. HA requires timezone-aware datetimes to ensure consistent behavior across installations in different timezones. The `coordinator.py` module uses `datetime.now()` in three locations:

1. **Line 577** — `last_hwinfo_update` timestamp for hardware info polling interval
2. **Line 606** — Same `last_hwinfo_update` on successful update
3. **Line 1551** — Uptime epoch calculation in `get_system_resource()`

These produce naive datetimes (no timezone info), which will trigger deprecation warnings in future HA releases and may cause incorrect calculations when the system timezone differs from UTC.

## Decision

Replace all `datetime.now()` calls with `homeassistant.util.dt.now()`, which returns timezone-aware datetimes using the HA instance's configured timezone.

For the uptime calculation (line 1551), the `datetime.timestamp()` call already converts to UTC epoch seconds, so the result is correct regardless — but using the HA utility ensures consistency and avoids deprecation warnings.

## Alternatives Considered

**1. Use `datetime.now(tz=datetime.timezone.utc)`**
Rejected — HA's `dt.now()` uses the configured timezone, which is the correct semantic for "current time" in an HA integration. UTC would work for internal comparisons but diverges from HA convention.

**2. Suppress deprecation warnings**
Rejected — the warnings exist for a reason. Future HA versions may enforce timezone-aware datetimes.

## Consequences

- Eliminates 3 naive datetime deprecation warnings
- Aligns with HA coding standards (`docs/ha-coding-standards.md`)
- Tracked as ISS-260320-deprecated-datetime
- No behavioral change in practice (all uses are relative time comparisons or epoch conversion)
