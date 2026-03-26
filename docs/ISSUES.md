# Issues — Mikrotik Router HACS Integration

## Current Priorities

1. ISS-260320-test-coverage — Increase test coverage to ≥80%
2. ISS-260320-new-device-discovery — New devices require HA restart to appear
3. ISS-260321-cognitive-complexity — Reduce cognitive complexity to ≤15 per function

---

## Active

### ISS-260320-test-coverage — Increase test coverage to ≥80%
**Type:** Testing
**Priority:** High
**Created:** 2026-03-20
**Status:** 🟡 Backlog — Phase 1-4 done, Phase 5 (full HA integration tests) pending

**Done:**
- ✅ Phase 1: `helper.py` (13 tests), `apiparser.py` (52 tests), `mikrotikapi.py` (30 tests), `coordinator.py` basics (12 tests) — PR #29
- ✅ Phase 2: coordinator data methods — get_system_resource, get_firmware_update, get_nat/mangle/filter, get_interface, get_dhcp, get_access (38 tests) — PR #29
- ✅ Phase 3: entity helpers — _skip_sensor, copy_attrs, MikrotikInterfaceEntityMixin (10 new tests), update.py pure functions (8 tests) — PR #29
- ✅ Phase 3.5: coordinator extracted helpers — 58 new tests for host merging, hostname resolution, accounting classification, captive portal, etc. — PR #30
- ✅ Phase 4: entity-level integration tests — 80 new tests covering all 6 platform entity types (sensor, binary_sensor, switch, button, device_tracker, update), MikrotikEntity base class, and init lifecycle — PR #31
- ✅ Devcontainer setup for local testing with pytest-homeassistant-custom-component — PR #29
- ✅ Ruff migration: all 32 source files pass lint and format — PR #29

**Remaining (Phase 5 — future PR):**
- Full HA integration tests: async_setup_entry, async_unload_entry (requires full HA platform machinery)
- Full coverage measurement and gap analysis

**Reference:** 461 tests passing (303 PR #29, 58 PR #30, 80 PR #31, 20 upstream FR port), target ≥80% for SonarCloud Grade A

---

## Backlog

### ISS-260321-cognitive-complexity — Reduce cognitive complexity to ≤15 per function
**Type:** Quality
**Priority:** High
**Created:** 2026-03-21
**Status:** 🟢 Active — PR #30 (feature/complexity-reduction → dev)

**Context:**
SonarCloud reports 14 functions exceeding cognitive complexity threshold of 15. Total project cognitive complexity is 1058. Worst offenders are upstream inherited code.

**Functions by severity:**
| Function | File | Complexity | Effort |
|----------|------|-----------|--------|
| `async_process_host()` | coordinator.py:2149 | 136 | 2h 6m |
| `_async_update_data()` (main) | coordinator.py:576 | 65 | 55m |
| `process_accounting()` | coordinator.py:2379 | 48 | 38m |
| `parse_api()` | apiparser.py:85 | 30 | 20m |
| `get_interface()` | coordinator.py:746 | 27 | 17m |
| `process_interface_client()` | coordinator.py:980 | 27 | 17m |
| `get_capabilities()` | coordinator.py:481 | 24 | 14m |
| `_skip_sensor()` | entity.py:75 | 23 | 13m |
| `async_process_host()` (tracker) | coordinator.py:1925 | 22 | 12m |
| `_async_update_data()` (tracker) | coordinator.py:149 | 21 | 11m |
| `extra_state_attributes` | switch.py:104 | 21 | 11m |
| `from_entry_bool()` | apiparser.py:55 | 18 | 16m |
| `query()` | mikrotikapi.py:189 | 18 | 8m |
| `get_system_resource()` | coordinator.py:1509 | 17 | 7m |

**Done (PR #29):**
- ✅ `get_system_resource()`: extracted `_parse_uptime_to_seconds()` helper
- ✅ `get_capabilities()`: consolidated duplicate wifi module branches

**Done (PR #30 — feature/complexity-reduction):**
- ✅ `async_process_host()` (136→~10 per helper): extracted `_merge_capsman_hosts`, `_merge_wireless_hosts`, `_merge_dhcp_hosts`, `_merge_arp_hosts`, `_recover_hass_hosts`, `_ensure_host_defaults`, `_update_host_availability`, `_update_host_address`, `_resolve_hostname`, `_dhcp_comment_for_host`, `_update_captive_portal`
- ✅ `_async_update_data()` (65→~15): extracted `_async_update_hwinfo`, `_run_if_enabled`, optional sensor loop tables
- ✅ `process_accounting()` (48→~10 per helper): extracted `_init_accounting_hosts`, `_classify_accounting_traffic`, `_check_accounting_threshold`, `_apply_accounting_throughput`
- ✅ `get_interface()` (27→~10): extracted `_monitor_ethernet_port` with `_SFP_MONITOR_VALS`, `_COPPER_MONITOR_VALS`, `_POE_MONITOR_VALS` class constants
- ✅ `_skip_sensor()` (23→~5 per helper): extracted `_skip_interface_traffic`, `_skip_binary_sensor`, `_skip_device_tracker`, `_skip_poe_sensor`
- ✅ `extra_state_attributes` switch.py (21→~5): reused `_copy_attrs` from entity.py
- ✅ `from_entry_bool()` (18→~8): extracted `_traverse_entry`, case-insensitive string matching via frozensets

**Remaining:**
- `process_interface_client()` (27) — not yet refactored
- `async_process_host()` tracker (22) — not yet refactored
- `_async_update_data()` tracker (21) — not yet refactored
- `query()` mikrotikapi.py (18) — not yet refactored

**Reference:** SonarCloud maintainability rating is A. 48 new tests cover extracted helpers.

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

### ISS-260320-refactor-dedup — Refactor duplicated patterns
**Type:** Refactoring
**Priority:** Medium
**Created:** 2026-03-20
**Status:** 🟡 Backlog

**Remaining:**
- coordinator.py: extract firewall rule dedup helper (get_nat/get_mangle/get_filter share ~75 LOC pattern)
- switch.py: extract base class for NAT/Mangle/Filter/Queue UID lookup (~50 LOC)
- ~~apiparser.py: extract shared path traversal from from_entry/from_entry_bool~~ ✅ Done in PR #30
- *_types.py: extract shared entity description base class (~80 LOC)

**Reference:** SonarCloud CPD exclusions already cover sensor_types.py and coordinator.py intentional repetition

---

### ISS-260321-silent-failures — Silent failure patterns from security audit
**Type:** Bug/Quality
**Priority:** Medium
**Created:** 2026-03-21
**Status:** 🟡 Backlog (partially addressed in PR #30)

**Context:**
Silent-failure audit (pr-review-toolkit:silent-failure-hunter) found 12 issues. Three critical/high items fixed in PR #30. Remaining items are pre-existing patterns.

**Fixed in PR #30:**
- ✅ `get_access()`: guard against KeyError when username not in router user list
- ✅ MAC vendor lookup: log failures at debug level instead of silently swallowing
- ✅ `_address_part_of_local_network()`: catch ValueError on malformed IPs

**Remaining:**
- switch.py: all `async_turn_on`/`async_turn_off` silently return when user lacks write access — should raise `HomeAssistantError` for UI feedback
- switch.py (NAT/Mangle/Filter/Queue): `value=None` silently passed to API when rule not found after UID lookup loop — should log error and return
- coordinator.py `get_queue()`: queue value parsing crashes on unexpected `split("/")` format — needs per-entry try/except
- coordinator.py `get_firmware_update()`: version parse failure lets integration limp with `major_fw_version=0`, silently disabling features
- entity.py `_handle_coordinator_update()`: KeyError if entity UID disappears from coordinator data
- switch.py `MikrotikPortSwitch`: unguarded bracket access on `self._data["about"]` and `self._data["port-mac-address"]`
- apiparser.py `from_entry()`: type coercion is identity operations (pre-existing)
- apiparser.py `get_uid()`: dead code on line 157 masks empty-key entries (pre-existing)

---

## Completed

### ISS-260326-slow-load — Startup bottlenecks blocking HA loading
**Type:** Bug/Performance | **Priority:** High | **Created:** 2026-03-26
**Status:** 🔴 Closed — fixed in v2.3.12 (claude/fix-homeassistant-slow-load)

### ISS-260320-deprecated-datetime — Remaining naive datetime.now() calls
**Type:** Bug | **Priority:** Medium | **Created:** 2026-03-20
**Status:** 🔴 Closed — fixed in v2.3.12 (claude/fix-homeassistant-slow-load)

### ISS-260325-attribute-bloat — ~1300 junk attributes on interface and tracker entities
**Type:** Bug/Quality | **Priority:** High | **Created:** 2026-03-25
**Status:** 🔴 Closed — fixed in v2.3.11-beta.1 (feature/attribute-cleanup)

### ISS-260325-mangle-dedup — Mangle rules with different interfaces removed as duplicates
**Type:** Bug | **Priority:** High | **Created:** 2026-03-25
**Status:** 🔴 Closed — fixed in PR #40 (fix/mangle-duplicate-interface)

### ISS-260324-arp-incomplete — ARP "incomplete" status incorrectly shows device as home
**Type:** Bug | **Priority:** High | **Created:** 2026-03-24
**Status:** 🔴 Closed — fixed in v2.3.10 (PR #38)

### ISS-260322-upstream-frs — Port upstream feature requests
**Type:** Feature | **Priority:** High | **Created:** 2026-03-22
**Status:** 🔴 Closed — released in v2.3.9 (PR #32)

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
