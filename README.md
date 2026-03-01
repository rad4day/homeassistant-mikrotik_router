# Mikrotik Router (Community Fork)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/jnctech/homeassistant-mikrotik_router?style=plastic)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=plastic)](https://github.com/hacs/integration)
![Project Stage](https://img.shields.io/badge/project%20stage-Production%20Ready-green.svg?style=plastic)
![GitHub all releases](https://img.shields.io/github/downloads/jnctech/homeassistant-mikrotik_router/total?style=plastic)

![GitHub commits since latest release](https://img.shields.io/github/commits-since/jnctech/homeassistant-mikrotik_router/latest?style=plastic)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/jnctech/homeassistant-mikrotik_router?style=plastic)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/jnctech/homeassistant-mikrotik_router/ci.yml?style=plastic)

> **This is a community-maintained fork of [tomaae/homeassistant-mikrotik_router](https://github.com/tomaae/homeassistant-mikrotik_router).** The original author built an incredible integration that many of us rely on daily. Life gets busy and open-source maintainers are volunteers -- we're grateful for all the work that went into this project. This fork exists to keep things running while the upstream repo is on a break, and we're happy to contribute fixes back anytime.

## Fix: Error 500 / Internal Server Error on Configure

If you are experiencing any of the following issues with the Mikrotik Router integration, this fork fixes them:

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
   * POE status, control and information
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
