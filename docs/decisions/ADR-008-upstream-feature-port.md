# ADR-008: Port Upstream Feature Requests (#310, #321, #334, #298)

**Date:** 2026-03-22
**Status:** Accepted

## Context

The upstream repository (tomaae/homeassistant-mikrotik_router) has several open feature requests that the community needs. Since the upstream repo is quiet, this fork implements them to keep the integration moving forward. The features were prototyped on a separate FR branch against `master`, then ported onto the refactored `dev` branch which has complexity reduction and 441 tests.

## Decision

Port four upstream feature requests into the fork:

### 1. Container Monitoring & Control (upstream #334)

- **API contract:** `/container` endpoint, keyed by `.id`
- **Entity identity:** Container `.id` (MikroTik internal ID)
- **Entity type:** Switch (start/stop via `execute` command, not `set_value`)
- **Capability detection:** Gated on `container` package being installed and enabled
- **Config option:** `sensor_container` (default: disabled)
- **Placement in update flow:** Standalone `if` block (requires both `support_container` AND `option_sensor_container`), after `optional_sensors_post` loop

### 2. Firewall RAW Switches (upstream #310)

- **API contract:** `/ip/firewall/raw` endpoint, keyed by `.id`
- **Entity identity:** Computed `uniq-id` via `val_proc` combine (same pattern as NAT/Mangle/Filter)
- **Entity type:** Switch (enable/disable via `set_value` on `disabled` parameter)
- **Config option:** `sensor_raw` (default: disabled)
- **Placement in update flow:** `optional_sensors` tuple list (single option guard, no capability check)
- **Deduplication:** Same pattern as NAT/Mangle/Filter — duplicate uniq-ids cause both entries to be removed

### 3. DHCP Client Sensors (upstream #321)

- **API contract:** Enriches existing `/ip/dhcp-client` endpoint with additional fields
- **Entity identity:** `interface` key (unchanged from existing)
- **Entity type:** Sensor (2 new descriptions: status and address)
- **New fields:** gateway, dns-server, dhcp-server, expires-after, comment
- **Always fetched:** No config option required (same as existing DHCP client data)

### 4. Environment Refresh After Script (upstream #298)

- **Change:** `await self.coordinator.async_refresh()` after `MikrotikScriptButton.async_press()`
- **Placement:** Outside try/except (refresh runs regardless of script success/failure)
- **Rationale:** Script execution may modify environment variables; immediate refresh reflects changes in UI

## Consequences

- Two new config options appear in the integration options flow
- Container support requires RouterOS 7.4+ with the container package installed
- RAW switch UID format string in `MikrotikRawSwitch` must exactly match the `val_proc` combine pattern — any mismatch results in silent failure (covered by tests)
- The `MikrotikRawSwitch` UID lookup follows the same duplicated pattern as NAT/Mangle/Filter/Queue; extracting a shared helper is deferred to ISS-260320-refactor-dedup
