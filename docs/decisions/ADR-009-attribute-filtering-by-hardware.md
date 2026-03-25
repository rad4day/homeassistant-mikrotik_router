# ADR-009: Entity Attribute Filtering by Hardware Capability

**Date:** 2026-03-25
**Status:** Accepted

## Context

All interface entities (sensors, binary sensors, switches, device trackers) displayed every attribute that `parse_api` returned, regardless of hardware type. Since `parse_api` always adds declared fields with default values, entities accumulated irrelevant attributes:

- SFP diagnostics (16 fields) on copper-only ports, all showing "unknown"
- `poe-out: "N/A"` on ports without PoE hardware
- `client-ip-address: "unknown"` on loopback, VLAN, PPPoE, WireGuard, bonding interfaces
- Wireless metrics (`signal-strength`, `tx-ccq`) on wired device tracker hosts
- Copper-specific fields (`rate`, `full-duplex`) missing from SFP ports

The root cause: `copy_attrs` checked only whether a key existed in `_data` (always true due to defaults), not whether the value was meaningful.

## Decision

### 1. Conditional attribute sets by hardware type

SFP and copper attribute lists are **mutually exclusive**. The `sfp-shutdown-temperature` field (fetched for all ethernet ports) determines which set applies:

- Value is non-zero/non-empty → SFP port → show `DEVICE_ATTRIBUTES_IFACE_SFP`
- Value is `0`/empty/absent → copper port → show `DEVICE_ATTRIBUTES_IFACE_ETHER`

Previously both lists were additive (ether always, then SFP on top).

### 2. Junk default filtering via `copy_attrs(skip_junk=True)`

A `skip_junk` keyword parameter on `copy_attrs` filters values matching `_JUNK_DEFAULTS` (`"unknown"`, `"none"`, `"N/A"`) and `None`. Applied to SFP and client attribute lists where defaults are commonly meaningless.

Values of `0`, `False`, and `""` are **not** filtered — these can be valid operational states (e.g. `link_downs: 0`, `running: false`).

### 3. Conditional attribute inclusion

| Attribute | Condition | Previously |
|-----------|-----------|------------|
| `poe-out` | Shown only when value is not `None`/`"N/A"`/`""` | Always shown on all ether ports |
| `client-ip-address`, `client-mac-address` | Shown only when value is meaningful (via `skip_junk`) | Always shown on all interfaces |
| Wireless metrics (`signal-strength`, `tx-ccq`, `tx-rate`, `rx-rate`) | Shown only for `source` in `("capsman", "wireless")` | Shown on all tracked hosts |

### 4. Single source of truth for attribute lists

`iface_attributes.py` is the canonical source. `switch_types.py` previously had duplicate copies; these are removed. `MikrotikPortSwitch` now inherits `MikrotikInterfaceEntityMixin` instead of duplicating the attribute logic.

### 5. SFP monitor parity with copper

Added `rate` and `full-duplex` to `_SFP_MONITOR_VALS` so SFP ports report link speed. Changed `sfp-temperature` default from `0` to `None` so empty SFP cages don't show a misleading temperature.

## Consequences

### Positive
- Entities only expose attributes relevant to their hardware
- Cleaner UI — no scrolling past 16 "unknown" SFP fields on copper ports
- SFP ports now show link rate (was missing entirely)

### Negative
- **Breaking change for automations** that relied on the presence of always-defaulted attributes (e.g. checking `state_attr('sensor.ether1_tx', 'sfp_temperature') != None`). These automations were likely unintentional since the values were always "unknown".
- Slightly more complex attribute selection logic in `MikrotikInterfaceEntityMixin`

### Neutral
- No entity identity changes (unique IDs, entity IDs unchanged)
- No change to the coordinator data model (`ds` dict still contains all keys)
- `copy_attrs` without `skip_junk` behaves identically to before (backward compatible)
