# Mikrotik Router Integration for Home Assistant (Community Fork)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/jnctech/homeassistant-mikrotik_router?style=plastic)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=plastic)](https://github.com/hacs/integration)
![Project Stage](https://img.shields.io/badge/project%20stage-Production%20Ready-green.svg?style=plastic)
![GitHub all releases](https://img.shields.io/github/downloads/jnctech/homeassistant-mikrotik_router/total?style=plastic)

![GitHub commits since latest release](https://img.shields.io/github/commits-since/jnctech/homeassistant-mikrotik_router/latest?style=plastic)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/jnctech/homeassistant-mikrotik_router?style=plastic)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/jnctech/homeassistant-mikrotik_router/ci.yml?style=plastic)

> **This is a community-maintained fork of [tomaae/homeassistant-mikrotik_router](https://github.com/tomaae/homeassistant-mikrotik_router).** The original author built an incredible integration that many of us rely on daily. Life gets busy and open-source maintainers are volunteers -- we're grateful for all the work that went into this project. This fork exists to keep things running while the upstream repo is on a break, and we're happy to contribute fixes back anytime.

## Dev Release Available for Testing

We have a **pre-release build** with several community-reported bug fixes ready for testing. If you're experiencing any of the issues below, please try the dev release and report back.

### What's fixed in the dev release

| Issue | Problem | Upstream ref |
|-------|---------|--------------|
| **Integration crash on non-wireless routers** | RB4011, RB5009, CCR routers crash because the integration queries wireless API endpoints on devices with no wireless hardware | [upstream #433](https://github.com/tomaae/homeassistant-mikrotik_router/issues/433) |
| **Temperature always shows Celsius** | Temperature sensors ignore HA unit preferences — users with imperial/Fahrenheit settings still see Celsius | [upstream #230](https://github.com/tomaae/homeassistant-mikrotik_router/issues/230) |
| **Error 500 on Configure** | Clicking "Configure" on the integration in HA 2025.12+ returns Internal Server Error | [upstream #464](https://github.com/tomaae/homeassistant-mikrotik_router/issues/464) |
| **WiFi package detection** | Correct detection of all RouterOS 7 WiFi package variants: `wifiwave2`, `wifi`, `wifi-qcom`, `wifi-qcom-ac` | — |

### How to install the dev release

1. In HACS, add this repo as a custom repository (if not already):
   - HACS > Integrations > 3-dot menu > Custom repositories
   - URL: `https://github.com/jnctech/homeassistant-mikrotik_router`
   - Category: Integration
2. In HACS, go to the Mikrotik Router integration and select **Redownload**
3. In the redownload dialog, enable **"Show beta versions"**
4. Select the latest pre-release version and install
5. Restart Home Assistant

### How to report results

Open an issue or comment on the relevant upstream issue. Even "works for me on RB5009 / RouterOS 7.16" is helpful — it tells us the fix is safe to ship.

---

## Fixes in the Current Stable Release

If you are experiencing any of the following issues with the Mikrotik Router integration, the stable release already fixes them:

- **Error 500 when clicking "Configure"** on the Mikrotik Router integration
- **Internal Server Error** when trying to change options for Mikrotik Router
- **"OptionsFlow has no attribute config_entry"** error in Home Assistant logs
- **AttributeError: property 'config_entry' of 'OptionsFlow' object has no setter** in HA 2025.12+
- **Mikrotik Router integration options page crashes** after updating Home Assistant
- **Cannot reconfigure Mikrotik Router** after Home Assistant 2025.12 update

This issue affects users of the original `tomaae/homeassistant-mikrotik_router` integration on **Home Assistant 2025.12 or later**.

### How to switch to this fork

If you installed the original via HACS:

1. Remove the original `tomaae/homeassistant-mikrotik_router` repository from HACS
2. Add this repository as a **custom repository** in HACS:
   - Go to HACS > Integrations > 3-dot menu > Custom repositories
   - Add `https://github.com/jnctech/homeassistant-mikrotik_router`
   - Category: Integration
3. Install **Mikrotik Router** from HACS
4. Restart Home Assistant

Your existing configuration and entities will be preserved -- no need to reconfigure.

If and when the upstream repo is updated, switching back is just as easy.

---

![Mikrotik Logo](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/header.png)

Monitor and control your Mikrotik device from Home Assistant.
 * Interfaces:
   * Enable/disable interfaces
   * SFP status and information
   * PoE-out per-port sensors: status, voltage, current and power consumption
   * PoE-in sensors: input voltage and current for PoE-powered devices
   * Monitor RX/TX traffic per interface
   * Monitor device presence per interface
   * IP, MAC, Link information per an interface for connected devices
 * Enable/disable NAT rule switches
 * Enable/disable Simple Queue switches
 * Enable/disable Mangle switches
 * Enable/disable Filter switches
 * Monitor and control PPP users
 * Monitor UPS
 * Monitor GPS coordinates
 * Captive Portal
 * Kid Control
 * Client Traffic RX/TX WAN/LAN monitoring though Accounting or Kid Control Devices (depending on RouterOS FW version)
 * Device tracker for hosts in network
 * System sensors (CPU, Memory, HDD, Temperature)
 * Check and update RouterOS and RouterBOARD firmware
 * Execute scripts
 * View environment variables
 * Configurable update interval
 * Configurable traffic unit (bps, Kbps, Mbps, B/s, KB/s, MB/s)
 * Supports monitoring of multiple mikrotik devices simultaneously

# Features
## Interfaces
Monitor and control status on each Mikrotik interface, both lan and wlan. Both physical and virtual.

![Interface Info](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/interface.png)
![Interface Switch](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/interface_switch.png)
![Interface Sensor](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/interface_sensor.png)

## PoE Monitoring
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

Not all PoE-capable hardware reports the same level of detail:

| Tier | Hardware examples | Sensors available |
|------|-------------------|-------------------|
| **Full monitoring** | CRS series managed switches, CSS series, hEX PoE | Status + voltage + current + power |
| **Status only** | hAP ax3 ether1 (passive 24 V PoE), some RB series ports | Status only |

On **status-only** ports the voltage, current and power sensors are automatically hidden because the hardware does not report those measurements. Only `poe-out-status` will appear.

To confirm your device capability, run in RouterOS terminal:
```
/interface ethernet poe monitor ether1 once
```
If the output includes `poe-out-voltage`, `poe-out-current` and `poe-out-power` fields, full monitoring is available. If only `poe-out-status` is returned, the port is status-only.

You can also check which ports have PoE configured:
```
/interface ethernet poe print
```

### PoE-Out sensors (per port)
Enable **PoE port sensors** in the integration options to add the following diagnostic sensors for each PoE-capable ethernet port:

| Sensor | Description | Example values | Hardware requirement |
|--------|-------------|----------------|---------------------|
| PoE out status | Current PoE port operational state | `powered-on`, `waiting-for-load`, `short-circuit`, `overload`, `voltage-too-low`, `off` | All PoE ports |
| PoE out voltage | Output voltage to the connected device | 48.0 V | Full monitoring only |
| PoE out current | Output current to the connected device | 120 mA | Full monitoring only |
| PoE out power | Power consumed by the connected device | 5.76 W | Full monitoring only |

Use `poe-out-status` in automations to detect PoE faults (overload, short-circuit) or trigger actions when a device is powered on or off. Combine `poe-out-power` with energy dashboards to track per-port power consumption on managed PoE switches such as the CRS series.

> **Note:** PoE port sensors are opt-in. Enable them under **Settings → Devices & Services → Mikrotik Router → Configure → PoE port sensors**. Sensors only appear for ports that report PoE capability (i.e. `poe-out` is set on the interface). Voltage, current and power sensors are automatically hidden on hardware that does not report those measurements. Implements [upstream feature request #259](https://github.com/tomaae/homeassistant-mikrotik_router/issues/259).

### How to enable and verify
1. Go to **Settings → Devices & Services → Mikrotik Router → Configure**
2. Check **PoE port sensors** and save
3. After the next poll cycle (default 60 s), new sensors appear under the **Interface** device for each PoE-capable port
4. Verify in **Developer Tools → States** by searching for `poe_out` — you should see entities such as `sensor.ether2_poe_out_status`, `sensor.ether2_poe_out_power`, etc.
5. If no sensors appear, check that the port has `poe-out` set in RouterOS (`/interface ethernet poe print`) and that a device is connected

### PoE-In sensors (system)
For MikroTik devices that are themselves powered via PoE, the following sensors appear automatically under the System device when the hardware reports them — no opt-in required:

| Sensor | Description |
|--------|-------------|
| PoE in voltage | Input voltage supplied to the device via PoE |
| PoE in current | Input current supplied to the device via PoE |

Example devices with PoE-In:
- **CRS310-8G+2S+IN** — management port accepts 802.3af/at (standard PoE) and passive PoE 18–57 V DC

PoE-In sensors only appear if your device exposes these values via `/system/health`. Not all PoE-powered devices support this command or report these measurements (for example, the hAP ac2 does not). Verify in RouterOS terminal:
```
/system health print
```
If the command returns `poe-in-voltage` and `poe-in-current` values, the sensors will appear. If the command gives a `bad command name health` error, your device does not support PoE-In monitoring.

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
Track availability of all network devices. All devices visible to Mikrotik device can be tracked, including: LAN connected devices and both Wireless and CAPsMAN from Mikrotik wireless package.

![Host tracker](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/host_tracker.png)

## Netwatch Tracking
Track netwatch status.

![Netwatch](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/netwatch_tracker.png)

## Scripts
Execute Mikrotik Router scripts.
You can execute scripts by automatically created switches or using services.

![Script Switch](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/script_switch.png)

## Kid Control
Monitor and control Kid Control.

![Kid Control Enable](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/kidcontrol_switch.png)
![Kid Control Pause](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/kidcontrol_pause_switch.png)

## Client Traffic

### Client Traffic for RouterOS v6
Monitor per-IP throughput tracking based on Mikrotik Accounting.

Feature is present in Winbox IP-Accounting. Make sure that threshold is set to reasonable value to store all connections between user defined scan interval. Max value is 8192 so for piece of mind I recommend setting that value.

More information about Accounting can be found on [Mikrotik support page](https://wiki.mikrotik.com/wiki/Manual:IP/Accounting).

NOTE: Accounting does not count in FastTracked packets.


### Client Traffic for RouterOS v7+
In RouterOS v7 Accounting feature is deprecated so alternative approach for is to use 
Kid Control Devices feature (IP - Kid Control - Devices).

This feature requires at least one 'kid' to be defined, 
after that Mikrotik will dynamically start tracking bandwidth usage of all known devices.

Simple dummy Kid entry can be defined with

```/ip kid-control add name=Monitor mon=0s-1d tue=0s-1d wed=0s-1d thu=0s-1d fri=0s-1d sat=0s-1d sun=0s-1d```

![Accounting sensor](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/accounting_sensor.png)

## UPS sensor
Monitor your UPS.

![UPS sensor](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/ups.png)

## GPS sensors
Monitor your GPS coordinates.

![GPS sensor](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/gps.png)

## Update sensor
Update Mikrotik OS and firmare directly from Home Assistant.

![RouterOS update](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/routeros_update.png)
![Firmware update](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/firmware_update.png)

# Install integration
This integration is distributed using [HACS](https://hacs.xyz/).

You can find it under "Integrations", named "Mikrotik Router"

Minimum requirements:
* RouterOS v6.43/v7.1
* Home Assistant 0.114.0

## Using Mikrotik development branch
If you are using development branch for mikrotik, some features may stop working due to major changes in RouterOS.
Use integration master branch instead of latest release to keep up with RouterOS beta adjustments.

## Setup integration
1. Create user for homeassistant on your mikrotik router with following permissions:
   * read, write, api, reboot, policy, test
   * lower permissions are supported, but it will limit functionality (read and api permissions are mandatory).
   * system health sensors won't be available without write & reboot permissions. this limitation is on mikrotik side.
2. If you want to be able to execute scripts on your mikrotik router from HA, script needs to have only following policies:
   * read, write
or check "Don't Require Permissions" option
3. Setup this integration for your Mikrotik device in Home Assistant via `Configuration -> Integrations -> Add -> Mikrotik Router`.
You can add this integration several times for different devices.

NOTES: 
- Do not mistake "Mikrotik Router" integration with HA build-in integration named "Mikrotik".
- If you dont see "Mikrotik Router" integration, clear your browser cache.

![Add Integration](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/setup_integration.png)
* "Name of the integration" - Friendly name for this router
* "Host" - Use hostname or IP
* "Port" - Leave at 0 for defaults

## Configuration
First options page:

![Integration options](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/integration_options.png)
* "Scan interval" - Scan/refresh time in seconds. HA needs to be reloaded for scan interval change to be applied
* "Unit of measurement" - Traffic sensor measurement (bps, Kbps, Mbps, B/s, KB/s, MB/s)
* "Show client MAC and IP on interfaces" - Display connected IP and MAC address for devices connected to ports on router
* "Track network devices timeout" - Tracked devices will be marked as away after timeout (does not apply to Mikrotik wireless and caps-man)
* "Zone for device tracker" - Add new tracked devices to a specified Home Assistant zone

Second options page:

![Integration sensors](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/integration_options_sensors.png)

Select sensors you want to use in Home Assistant.

# Known Issues & Workarounds

## Wireless clients always showing 0 (hAP ac2, hAP ax2, hAP ax3, Audience, RouterOS 7.x)

**Affected devices:** hAP ac2, hAP ax2, hAP ax3, Audience, and any MikroTik device using the newer **WiFi package** (not the legacy **Wireless package**).

**What's happening:** MikroTik introduced a new WiFi system starting with 802.11ax (WiFi 6) devices. The newer WiFi package uses different API endpoints (`/interface/wifi`) compared to the legacy Wireless package (`/interface/wireless`). The integration currently only queries the legacy endpoints, so wireless client counts return 0 on newer devices.

**Workaround — use Kid Control for device tracking:**

This gives you per-device tracking and bandwidth monitoring even when wireless client counts don't work.

1. SSH or open a terminal to your MikroTik router
2. Create a dummy Kid Control entry that covers all days:
```
/ip kid-control add name=Monitor mon=0s-1d tue=0s-1d wed=0s-1d thu=0s-1d fri=0s-1d sat=0s-1d sun=0s-1d
```
3. MikroTik will now automatically track all known devices under **IP > Kid Control > Devices**
4. In the integration options (Configure), enable **"Track network devices"**
5. Reload the integration

This gives you device presence detection and per-client traffic stats via Kid Control Devices, bypassing the broken wireless client counter entirely.

**Status:** We're looking at adding support for the new WiFi package API endpoints in a future release ([upstream #421](https://github.com/tomaae/homeassistant-mikrotik_router/issues/421)).

## Integration crashes on routers without wireless package (RB4011, RB5009, CCR series)

**Affected devices:** RB4011, RB5009, CCR1009, CCR1016, CCR1036, CCR2004, CCR2116, and any MikroTik router where the wireless package is absent or disabled.

**What's happening:** On RouterOS 7+, the integration unconditionally queries wireless API endpoints (`/interface/wireless`, `/caps-man/registration-table`) even on devices that have no wireless hardware. This causes the integration to crash on startup.

**Status:** Fixed in the [dev release](#dev-release-available-for-testing). The fix correctly checks which WiFi packages are installed before querying wireless endpoints. Please test and report back so we can ship it in the next stable release. ([upstream #433](https://github.com/tomaae/homeassistant-mikrotik_router/issues/433))

## MikroTik temperature sensors always show Celsius, ignore Fahrenheit preference

**Affected users:** Anyone with Home Assistant configured for imperial units (Fahrenheit).

**What's happening:** Temperature sensors (CPU temperature, board temperature, switch temperature, PHY temperature) always display in Celsius even when your HA instance is set to Fahrenheit. The sensors were overriding HA's automatic unit conversion.

**Status:** Fixed in the [dev release](#dev-release-available-for-testing). Temperature sensors now respect your HA unit preference and auto-convert between Celsius and Fahrenheit. ([upstream #230](https://github.com/tomaae/homeassistant-mikrotik_router/issues/230))

---

# Development

## Translation
To help out with the translation you need an account on Lokalise, the easiest way to get one is to [click here](https://lokalise.com/login/) then select "Log in with GitHub".
After you have created your account [click here to join Mikrotik Router project on Lokalise](https://app.lokalise.com/public/581188395e9778a6060128.17699416/).

If you want to add translations for a language that is not listed please [open a Feature request](https://github.com/tomaae/homeassistant-mikrotik_router/issues/new?labels=enhancement&title=%5BLokalise%5D%20Add%20new%20translations%20language).

## Diagnostics
Download diagnostics data for investigation:

![Diagnostics](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/diagnostics.png)

## Enabling debug
To enable debug for Mikrotik router integration, add following to your configuration.yaml:
```
logger:
  default: info
  logs:
    custom_components.mikrotik_router: debug
```
