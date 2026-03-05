# MikroTik Router Integration for Home Assistant

![GitHub release (latest by date)](https://img.shields.io/github/v/release/jnctech/homeassistant-mikrotik_router?style=plastic)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=plastic)](https://github.com/hacs/integration)
![Project Stage](https://img.shields.io/badge/project%20stage-Production%20Ready-green.svg?style=plastic)
![GitHub all releases](https://img.shields.io/github/downloads/jnctech/homeassistant-mikrotik_router/total?style=plastic)

![GitHub commits since latest release](https://img.shields.io/github/commits-since/jnctech/homeassistant-mikrotik_router/latest?style=plastic)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/jnctech/homeassistant-mikrotik_router?style=plastic)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/jnctech/homeassistant-mikrotik_router/ci.yml?style=plastic)

Monitor and control your entire MikroTik network from Home Assistant. This HACS integration connects to MikroTik routers, switches and access points running RouterOS v6 or v7, surfacing interface status, PoE monitoring, traffic sensors, wireless client counts, network device tracking, system health, firmware updates and more — all as native Home Assistant entities on a configurable polling interval.

> **This is a community-maintained fork of [tomaae/homeassistant-mikrotik_router](https://github.com/tomaae/homeassistant-mikrotik_router).** The original author built an incredible integration that many of us rely on daily. This fork exists to keep things running and ship bug fixes while the upstream repo is quiet. We're happy to contribute fixes back anytime.

---

## What's New — v2.3.3

The [v2.3.3](https://github.com/jnctech/homeassistant-mikrotik_router/releases/tag/v2.3.3) release is the first stable release of this community fork. It adds a major new feature and fixes several long-standing bugs reported against the upstream integration.

### New feature: PoE monitoring

Monitor Power over Ethernet status and power metrics for each PoE-capable port on your MikroTik switch or router directly in Home Assistant. Enable **PoE port sensors** under **Settings → Devices & Services → Mikrotik Router → Configure**.

| Sensor | Description | Hardware |
|--------|-------------|----------|
| PoE out status | Port operational state (`powered-on`, `waiting-for-load`, `overload`, etc.) | All PoE ports |
| PoE out voltage | Output voltage to connected device | Full monitoring hardware (CRS/CSS/hEX PoE) |
| PoE out current | Output current to connected device | Full monitoring hardware (CRS/CSS/hEX PoE) |
| PoE out power | Power consumed by connected device | Full monitoring hardware (CRS/CSS/hEX PoE) |

Voltage, current and power sensors are **automatically hidden** on passive-PoE hardware that does not report measurements (e.g. hAP ax3 ether1). Only `poe-out-status` appears on those ports.

### Bug fixes in v2.3.3

| Fix | Detail |
|-----|--------|
| **Error 500 on Configure** | Fixed for HA 2025.12+ — `OptionsFlow` compatibility with the new framework ([#464](https://github.com/tomaae/homeassistant-mikrotik_router/issues/464)) |
| **Integration crash on non-wireless routers** | RB4011, RB5009, CCR series no longer fail on startup when wireless package is absent ([#433](https://github.com/tomaae/homeassistant-mikrotik_router/issues/433)) |
| **Wired client count always 0** | ARP/DHCP hosts now correctly marked available — wired client counter works ([upstream #468](https://github.com/tomaae/homeassistant-mikrotik_router/issues/468)) |
| **Wireless client count** | Correct client count on hAP ac2 and compatible devices ([upstream #421](https://github.com/tomaae/homeassistant-mikrotik_router/issues/421)) |
| **Temperature sensors ignore Fahrenheit preference** | Sensors now respect the HA unit preference ([#230](https://github.com/tomaae/homeassistant-mikrotik_router/issues/230)) |
| PoE measurement sensors showing 0 on passive PoE ports | Voltage/current/power sensors now hidden when hardware does not report measurements |
| RouterOS 7 WiFi package detection | Supports `wifiwave2`, `wifi`, `wifi-qcom`, `wifi-qcom-ac` |

### Install via HACS

1. In HACS, add this repo as a custom repository (if not already):
   - HACS > Integrations > 3-dot menu > Custom repositories
   - URL: `https://github.com/jnctech/homeassistant-mikrotik_router`
   - Category: Integration
2. Install **Mikrotik Router** from HACS
3. Restart Home Assistant

### Switching from the upstream fork

If you are currently on `tomaae/homeassistant-mikrotik_router` and seeing **Error 500 on Configure**, **Internal Server Error**, or **crashes on startup** since updating Home Assistant:

1. Remove `tomaae/homeassistant-mikrotik_router` from HACS custom repositories
2. Add `https://github.com/jnctech/homeassistant-mikrotik_router` as a custom repository in HACS
3. Install **Mikrotik Router** from HACS and restart Home Assistant

Your existing configuration and entities are preserved — no reconfiguration needed.

---

![Mikrotik Logo](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/header.png)

## Feature Highlights

- **Interfaces** — enable/disable, SFP info, RX/TX traffic, connected device IP/MAC, interface presence
- **PoE monitoring** *(new in v2.3.x)* — per-port status, voltage, current and power for PoE-capable switches
- **NAT rules** — enable/disable individual rules
- **Mangle rules** — enable/disable individual rules
- **Filter rules** — enable/disable individual rules
- **Simple Queues** — control bandwidth queues
- **PPP users** — monitor and control PPP connections
- **Host tracking** — presence detection for all LAN, wireless and CAPsMAN devices
- **Netwatch** — track netwatch probe status
- **Client traffic** — per-client RX/TX via Accounting (RouterOS v6) or Kid Control Devices (RouterOS v7)
- **System sensors** — CPU, memory, HDD, temperature (Celsius/Fahrenheit)
- **System health** — PoE-in voltage/current on supported hardware, UPS, environment sensors
- **Firmware updates** — check and update RouterOS and RouterBOARD firmware from HA
- **Scripts** — execute RouterOS scripts from HA
- **GPS** — monitor GPS coordinates
- **Kid Control** — monitor and control internet schedules
- **Multiple devices** — monitor several MikroTik devices simultaneously

---

# Features

## Interfaces
Monitor and control status on each MikroTik interface — LAN, WLAN, physical and virtual.

![Interface Info](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/interface.png)
![Interface Switch](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/interface_switch.png)
![Interface Sensor](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/interface_sensor.png)

## PoE Monitoring *(new — v2.3.x pre-release)*
Monitor Power over Ethernet (PoE) status and power metrics for each PoE-capable port on your MikroTik switch or router directly in Home Assistant.

More information about PoE-Out can be found on the [MikroTik support page](https://help.mikrotik.com/docs/display/ROS/PoE-Out).

### Compatible hardware
PoE-Out sensors are available on MikroTik devices with managed PoE-Out ports, including (but not limited to):

- **CRS series** managed switches: CRS106, CRS112, CRS210, CRS212, CRS226, CRS317, CRS328, CRS354, **CRS310-8G+2S+IN**
- **CSS series** with PoE: CSS106, CSS326, CSS610
- **RB series** with PoE-Out: RB260, RB2011, RB3011, RB4011, RB5009
- **hEX PoE**, **hEX PoE lite**
- Any RouterOS device where `/interface/ethernet/poe` returns data

#### Two tiers of PoE-Out monitoring

| Tier | Hardware examples | Sensors available |
|------|-------------------|-------------------|
| **Full monitoring** | CRS series managed switches, CSS series, hEX PoE | Status + voltage + current + power |
| **Status only** | hAP ax3 ether1 (passive 24 V PoE), some RB series ports | Status only |

On **status-only** ports the voltage, current and power sensors are automatically hidden because the hardware does not report those measurements. Only `poe-out-status` will appear.

To confirm your device capability, run in RouterOS terminal:
```
/interface ethernet poe monitor ether1 once
```

### PoE-Out sensors (per port)
Enable **PoE port sensors** in the integration options to add the following diagnostic sensors for each PoE-capable ethernet port:

| Sensor | Description | Example values | Hardware requirement |
|--------|-------------|----------------|---------------------|
| PoE out status | Current PoE port operational state | `powered-on`, `waiting-for-load`, `short-circuit`, `overload`, `voltage-too-low`, `off` | All PoE ports |
| PoE out voltage | Output voltage to the connected device | 48.0 V | Full monitoring only |
| PoE out current | Output current to the connected device | 120 mA | Full monitoring only |
| PoE out power | Power consumed by the connected device | 5.76 W | Full monitoring only |

> **Note:** PoE port sensors are opt-in. Enable them under **Settings → Devices & Services → Mikrotik Router → Configure → PoE port sensors**. Voltage, current and power sensors are automatically hidden on hardware that does not report those measurements. Implements [upstream feature request #259](https://github.com/tomaae/homeassistant-mikrotik_router/issues/259).

### PoE-In sensors (system)
For MikroTik devices powered via PoE, the following sensors appear automatically under the System device when the hardware reports them — no opt-in required:

| Sensor | Description |
|--------|-------------|
| PoE in voltage | Input voltage supplied to the device via PoE |
| PoE in current | Input current supplied to the device via PoE |

Example devices with PoE-In:
- **CRS310-8G+2S+IN** — management port accepts 802.3af/at (standard PoE) and passive PoE 18–57 V DC

PoE-In sensors only appear if your device exposes these values via `/system/health`. Not all PoE-powered devices support this command (e.g. hAP ac2 returns `bad command name health`). Verify with `/system health print` in RouterOS terminal.

## NAT
Monitor and control individual NAT rules.

More information about NAT rules can be found on [Mikrotik support page](https://help.mikrotik.com/docs/display/ROS/NAT).

![NAT switch](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/nat.png)

## Mangle
Monitor and control individual Mangle rules.

More information about Mangle rules can be found on [Mikrotik support page](https://help.mikrotik.com/docs/display/ROS/Mangle).

![Mangle switch](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/mangle_switch.png)


## Simple Queue
Control simple queues.

More information about simple queues can be found on [Mikrotik support page](https://help.mikrotik.com/docs/display/ROS/Queues#heading-SimpleQueue).

NOTE: FastTracked packets are not processed by Simple Queues.

![Queue switch](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/queue_switch.png)


## PPP
Control and monitor PPP users.

![PPP switch](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/ppp_switch.png)
![PPP tracker](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/ppp_tracker.png)

## Host Tracking
Track availability of all network devices. All devices visible to the MikroTik device can be tracked, including LAN connected devices and both Wireless and CAPsMAN clients.

![Host tracker](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/host_tracker.png)

## Netwatch Tracking
Track netwatch probe status.

![Netwatch](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/netwatch_tracker.png)

## Scripts
Execute MikroTik Router scripts from Home Assistant via automatically created switches or services.

![Script Switch](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/script_switch.png)

## Kid Control
Monitor and control Kid Control internet schedules.

![Kid Control Enable](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/kidcontrol_switch.png)
![Kid Control Pause](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/kidcontrol_pause_switch.png)

## Client Traffic

### Client Traffic for RouterOS v6
Monitor per-IP throughput based on MikroTik Accounting (Winbox: IP → Accounting).

Set the threshold to a reasonable value — max is 8192. FastTracked packets are not counted.

More information: [MikroTik Accounting](https://wiki.mikrotik.com/wiki/Manual:IP/Accounting).

### Client Traffic for RouterOS v7+
In RouterOS v7 the Accounting feature is deprecated. Use Kid Control Devices instead (IP → Kid Control → Devices). Requires at least one Kid entry to be defined — a dummy entry works:

```
/ip kid-control add name=Monitor mon=0s-1d tue=0s-1d wed=0s-1d thu=0s-1d fri=0s-1d sat=0s-1d sun=0s-1d
```

![Accounting sensor](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/accounting_sensor.png)

## UPS sensor
Monitor your UPS.

![UPS sensor](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/ups.png)

## GPS sensors
Monitor GPS coordinates.

![GPS sensor](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/gps.png)

## Update sensor
Check and update RouterOS and RouterBOARD firmware directly from Home Assistant.

![RouterOS update](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/routeros_update.png)
![Firmware update](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/firmware_update.png)

---

# Install Integration

This integration is distributed using [HACS](https://hacs.xyz/).

**Minimum requirements:**
- RouterOS v6.43 or v7.1+
- Home Assistant 0.114.0+

## Setup

1. Create a dedicated Home Assistant user on your MikroTik device with these permissions:
   - `read, write, api, reboot, policy, test`
   - `read` and `api` are mandatory; lower permissions will limit functionality
   - System health sensors require `write` and `reboot` (MikroTik limitation)
2. For script execution, the script itself needs only `read, write` — or check "Don't Require Permissions"
3. Add the integration: **Settings → Devices & Services → Add Integration → Mikrotik Router**

> Do not confuse "Mikrotik Router" with the built-in Home Assistant "Mikrotik" integration. If you don't see it, clear your browser cache.

![Add Integration](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/setup_integration.png)

## Configuration options

![Integration options](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/integration_options.png)

- **Scan interval** — poll frequency in seconds (HA reload required after change)
- **Unit of measurement** — traffic sensor units: bps, Kbps, Mbps, B/s, KB/s, MB/s
- **Show client MAC and IP on interfaces** — display connected device info per port
- **Track network devices timeout** — mark tracked devices away after this period
- **Zone for device tracker** — assign new tracked devices to a Home Assistant zone

![Integration sensors](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/integration_options_sensors.png)

---

# Known Issues & Workarounds

## Wireless clients count (hAP ax2, hAP ax3, Audience, RouterOS 7 WiFi package)

**Affected devices:** hAP ax2, hAP ax3, Audience, and devices using the newer **WiFi package** (not the legacy **Wireless package**).

**What's happening:** Devices running the newer WiFi package (802.11ax/WiFi 6 hardware) use `/interface/wifi` API endpoints instead of the legacy `/interface/wireless`. The `sensor.*_wireless_clients_api` sensor works correctly on legacy Wireless package devices (confirmed on hAP ac2). Devices on the newer WiFi package may report 0.

**Workaround — use Kid Control for device tracking:**

1. SSH or open a terminal to your MikroTik router
2. Create a dummy Kid Control entry:
```
/ip kid-control add name=Monitor mon=0s-1d tue=0s-1d wed=0s-1d thu=0s-1d fri=0s-1d sat=0s-1d sun=0s-1d
```
3. In integration options, enable **"Track network devices"**
4. Reload the integration

This provides device presence detection and per-client traffic stats regardless of WiFi package version.

**Status:** Native support for the new WiFi package API is planned ([upstream #421](https://github.com/tomaae/homeassistant-mikrotik_router/issues/421)).

## Integration crashes on routers without wireless package (RB4011, RB5009, CCR series)

**Affected devices:** RB4011, RB5009, CCR1009, CCR1016, CCR1036, CCR2004, CCR2116, and any MikroTik router where the wireless package is absent.

**Status:** Fixed in the [v2.3.x pre-release](#whats-new--v23x-pre-release). The fix checks which WiFi packages are installed before querying wireless endpoints. ([upstream #433](https://github.com/tomaae/homeassistant-mikrotik_router/issues/433))

## Temperature sensors always show Celsius, ignore Fahrenheit preference

**Affected users:** Home Assistant instances configured for imperial/Fahrenheit units.

**Status:** Fixed in the [v2.3.x pre-release](#whats-new--v23x-pre-release). Temperature sensors now respect HA unit preferences and auto-convert. ([upstream #230](https://github.com/tomaae/homeassistant-mikrotik_router/issues/230))

---

# Development

## Translation
To help with translation, [log in to Lokalise with GitHub](https://lokalise.com/login/) then [join the Mikrotik Router project](https://app.lokalise.com/public/581188395e9778a6060128.17699416/).

To request a new language, [open a Feature request](https://github.com/tomaae/homeassistant-mikrotik_router/issues/new?labels=enhancement&title=%5BLokalise%5D%20Add%20new%20translations%20language).

## Diagnostics
Download diagnostics data for investigation:

![Diagnostics](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/diagnostics.png)

## Enabling debug logging
Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.mikrotik_router: debug
```
