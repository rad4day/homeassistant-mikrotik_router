# Architecture Notes

## Core Components

| File | Role | Notes |
|------|------|-------|
| `coordinator.py` | Data polling (~102KB) | Largest file, all RouterOS queries |
| `mikrotikapi.py` | API client wrapper | Wraps `librouteros`, shared `threading.Lock` |
| `apiparser.py` | Response parser | Transforms raw API responses |
| `config_flow.py` | Setup + options UI | Uses `OptionsFlowWithConfigEntry` |
| `entity.py` | Base entity classes | Common properties, device info |

## Two Coordinators

- **MikrotikCoordinator** (30s) — system data, interfaces, firewall, sensors
- **MikrotikTrackerCoordinator** (10s) — device presence tracking

Both share a mutable `ds` dict. Safe in single-threaded async, but fragile if `asyncio.gather()` or executor jobs are introduced.

## API Client Locking

All `MikrotikAPI` methods use a shared `threading.Lock`. Every method must acquire/release via context manager (`with self.lock:`). Manual acquire/release has caused deadlock bugs.

## RouterOS Compatibility

- v6 and v7 have different wireless API paths
- Supported packages: `wireless`, `wifiwave2`, `wifi`, `wifi-qcom`, `wifi-qcom-ac`
- Non-wireless routers (RB4011, RB5009, CCR) need package checks before wireless queries

## Coordinator Helper Structure (ADR-007)

Large coordinator methods have been decomposed into focused helpers. Each helper handles one responsibility and is independently testable.

**Host processing** (`async_process_host` orchestrates):
- `_merge_capsman_hosts()`, `_merge_wireless_hosts()`, `_merge_dhcp_hosts()`, `_merge_arp_hosts()` — source-specific host merging
- `_recover_hass_hosts()` — one-time HA registry recovery
- `_ensure_host_defaults()` — fill missing keys from `_HOST_DEFAULTS`
- `_update_host_availability()`, `_update_host_address()` — per-host state
- `_resolve_hostname()` → `_hostname_from_dns()`, `_hostname_from_dhcp()`, `_dhcp_comment_for_host()`
- `_update_captive_portal()` — hotspot data sync

**Update cycle** (`_async_update_data` orchestrates):
- `_async_update_hwinfo()` — 4-hourly hardware info refresh
- `_async_run_if_connected()` — guarded executor dispatch

**Accounting** (`process_accounting` orchestrates):
- `_init_accounting_hosts()`, `_classify_accounting_traffic()`, `_check_accounting_threshold()`, `_apply_accounting_throughput()`
- `_add_traffic_bytes()` — static method for WAN/LAN bucket classification

**Interface monitoring**:
- `_monitor_ethernet_port()` — SFP/copper/PoE monitor with `_SFP_MONITOR_VALS`, `_COPPER_MONITOR_VALS`, `_POE_MONITOR_VALS` class constants

**Entity skip logic** (`_skip_sensor` orchestrates):
- `_skip_interface_traffic()`, `_skip_binary_sensor()`, `_skip_device_tracker()`, `_skip_poe_sensor()`

## Attribute Selection Patterns (ADR-009)

Entity attributes are filtered by hardware capability to avoid displaying meaningless defaults.

**`copy_attrs(skip_junk=True)`** — filters `"unknown"`, `"none"`, `"N/A"`, and `None` values. Does NOT filter `0`, `False`, or `""` (valid operational states). Used for SFP diagnostics and client IP/MAC attributes.

**`MikrotikInterfaceEntityMixin`** — shared mixin for `MikrotikInterfaceTrafficSensor`, `MikrotikPortBinarySensor`, and `MikrotikPortSwitch`. Selects attribute set based on interface type:

| Interface type | Detection | Attribute list |
|----------------|-----------|----------------|
| Copper ethernet | `sfp-shutdown-temperature` is `0`/empty/absent | `DEVICE_ATTRIBUTES_IFACE_ETHER` |
| SFP ethernet | `sfp-shutdown-temperature` has real value | `DEVICE_ATTRIBUTES_IFACE_SFP` (with `skip_junk`) |
| Wireless | `type == "wlan"` | `DEVICE_ATTRIBUTES_IFACE_WIRELESS` |

Additionally:
- `client-ip-address`/`client-mac-address` — shown only when meaningful (via `DEVICE_ATTRIBUTES_IFACE_CLIENT` + `skip_junk`)
- `poe-out` — shown only when port has PoE support (not `"N/A"`)
- Wireless metrics (`signal-strength`, `tx-ccq`, `tx/rx-rate`) — shown only for wireless/CAPsMAN hosts in device tracker

**Canonical attribute lists** live in `iface_attributes.py`. All entity types import from there (no duplicates).

## Known Caveats

- `ds` dict shared between coordinators (mutation overlap risk)
- `coordinator.py` size — refactoring into smaller modules is desirable but risky
- RouterOS accounting API differs between v6 (IP accounting) and v7 (Kid Control)
