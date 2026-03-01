# Issues to create on jnctech/homeassistant-mikrotik_router

Create these at: https://github.com/jnctech/homeassistant-mikrotik_router/issues/new

---

## Issue 1: Integration crashes on routers without wireless package (RB4011, RB5009, CCR series)

**Labels:** bug, upstream

### Title
Integration crashes on routers without wireless package (upstream #433)

### Body
**Upstream reference:** tomaae/homeassistant-mikrotik_router#433

**Affected devices:** RB4011, RB5009, CCR series, and any router where the wireless package is disabled or absent.

**Problem:** On RouterOS 7+, the integration unconditionally sets `support_wireless = True` and then tries to query wireless API endpoints (`/interface/wireless`, `/caps-man/registration-table`) that don't exist on non-wireless devices. This causes the integration to fail entirely.

**Root cause:** In `coordinator.py` `get_capabilities()`, the v7+ branch set `support_wireless = True` before checking which wifi package (if any) was actually installed.

**Fix:** Only enable `support_wireless` when a wifi package is actually found and enabled in the device's package list. Check for all known variants: `wifiwave2`, `wifi`, `wifi-qcom`, `wifi-qcom-ac`, and legacy `wireless`.

**Status:** Fix implemented in branch `claude/fix-433-wireless-crash-SU7Jp`

---

## Issue 2: Temperature sensors ignore user's unit preference (always show Celsius)

**Labels:** bug, upstream

### Title
Temperature sensors ignore HA unit preference - always display Celsius (upstream #230)

### Body
**Upstream reference:** tomaae/homeassistant-mikrotik_router#230

**Problem:** Temperature sensors (CPU, board, switch, PHY, system) always display in Celsius regardless of the user's Home Assistant unit system preference. Users who have HA configured for Fahrenheit still see Celsius values.

**Root cause:** The temperature sensor definitions in `sensor_types.py` set `suggested_unit_of_measurement=UnitOfTemperature.CELSIUS`, which overrides HA's automatic unit conversion. Since these sensors already have `device_class=SensorDeviceClass.TEMPERATURE` and `native_unit_of_measurement=UnitOfTemperature.CELSIUS`, HA will automatically handle C-to-F conversion when the user's unit system is imperial.

**Fix:** Remove `suggested_unit_of_measurement` from the 5 temperature sensor definitions. The `device_class` and `native_unit_of_measurement` are sufficient for HA to auto-convert.

**Affected sensors:** system_temperature, system_cpu-temperature, system_switch-temperature, system_board-temperature1, system_phy-temperature

**Status:** Fix implemented in branch `claude/fix-230-temperature-units-SU7Jp`

---

## Issue 3: New WiFi package API not supported (hAP ac2, hAP ax2/3, Audience)

**Labels:** enhancement, upstream

### Title
Support new WiFi package API endpoints for wireless client tracking (upstream #421)

### Body
**Upstream reference:** tomaae/homeassistant-mikrotik_router#421

**Affected devices:** hAP ac2, hAP ax2, hAP ax3, Audience, and any device using MikroTik's newer WiFi package (not the legacy Wireless package).

**Problem:** MikroTik introduced a new WiFi system for 802.11ax (WiFi 6) devices. The newer WiFi package uses `/interface/wifi` API endpoints instead of legacy `/interface/wireless`. The integration only queries legacy endpoints, so wireless client counts return 0.

**Workaround:** Use Kid Control for device tracking - create a dummy Kid Control entry and enable "Track network devices" in integration options. See README for details.

**What's needed:** Add support for querying `/interface/wifi/registration-table` on devices with the new WiFi package.

---

## Issue 4: Integration fails querying CAPsMAN on routers without wireless

**Labels:** bug, upstream

### Title
Integration queries /caps-man/registration-table on non-wireless routers (related to upstream #433)

### Body
**Upstream reference:** Related to tomaae/homeassistant-mikrotik_router#433

**Problem:** The integration attempts to query `/caps-man/registration-table` (or `/interface/wifi/registration-table` on v7.13+) even on routers that don't have any wireless capability. This is related to #433 but specifically about the CAPsMAN component.

**Root cause:** `support_capsman` defaults are not properly handled in the v7+ package detection path when no wireless package is present.

**Fix:** Included in the fix for issue #1 (branch `claude/fix-433-wireless-crash-SU7Jp`) - when no wireless package is found, both `support_wireless` and `support_capsman` remain `False` (their default values).

---

## Issue 5: Error 500 / Internal Server Error when clicking Configure (HA 2025.12+)

**Labels:** bug, fixed

### Title
Error 500 on Configure page with Home Assistant 2025.12+ (upstream #464)

### Body
**Upstream reference:** tomaae/homeassistant-mikrotik_router#464

**Problem:** After upgrading to Home Assistant 2025.12 or later, clicking "Configure" on the Mikrotik Router integration produces an HTTP 500 Internal Server Error. The HA logs show:
- `OptionsFlow has no attribute config_entry`
- `AttributeError: property 'config_entry' of 'OptionsFlow' object has no setter`

**Root cause:** HA 2025.12 changed `config_entry` from a writable attribute to a read-only property on `OptionsFlow`. The integration's `MikrotikControllerOptionsFlowHandler` needs to use `OptionsFlowWithConfigEntry` and pass the config entry to its constructor.

**Fix:** Changed base class from `OptionsFlow` to `OptionsFlowWithConfigEntry` and pass `config_entry` in `async_get_options_flow()`.

**Status:** Fixed in v2.2.3

---

## Issue 6: Stringly-typed package names make maintenance error-prone

**Labels:** code quality, enhancement

### Title
Extract RouterOS package names to constants to reduce typo risk

### Body
**Problem:** RouterOS package names (`wireless`, `wifiwave2`, `wifi`, `wifi-qcom`, `wifi-qcom-ac`, `ups`, `gps`) are scattered as raw string literals throughout `coordinator.py`. When MikroTik adds new package variants (as they've done multiple times), every string must be found and updated manually, with typo risk.

**Fix:** Added `PKG_*` constants to `const.py` and a `_pkg_enabled()` helper function to replace the repeated pattern of `"name" in packages and packages["name"]["enabled"]`.

**Status:** Fixed in branch `claude/fix-433-wireless-crash-SU7Jp` as part of the wireless detection refactor.
