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

## Known Caveats

- `ds` dict shared between coordinators (mutation overlap risk)
- `coordinator.py` size — refactoring into smaller modules is desirable but risky
- RouterOS accounting API differs between v6 (IP accounting) and v7 (Kid Control)
