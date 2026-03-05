Monitor and control your MikroTik router from Home Assistant.

**Community-maintained fork** with active bug fixes for HA 2025.12+ compatibility, RouterOS 7 support, and more.

![Mikrotik Logo](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/ui/header.png)

### What's new in v2.3.3
- **PoE monitoring** — per-port PoE-Out sensors (status, voltage, current, power) for CRS/RB/hEX PoE switches; PoE-In sensors for PoE-powered devices ([#259](https://github.com/tomaae/homeassistant-mikrotik_router/issues/259))
- **Wired client count fix** — `clients_wired` now correctly counts wired devices ([upstream #468](https://github.com/tomaae/homeassistant-mikrotik_router/issues/468))
- **RB4011 / RB5009 / CCR crash fix** — integration no longer fails on routers without wireless package ([#433](https://github.com/tomaae/homeassistant-mikrotik_router/issues/433))
- **Temperature unit conversion** — sensors now respect Fahrenheit preference ([#230](https://github.com/tomaae/homeassistant-mikrotik_router/issues/230))
- **Error 500 on Configure** — fixed for HA 2025.12+ ([#464](https://github.com/tomaae/homeassistant-mikrotik_router/issues/464))
- **WiFi package detection** — supports wifiwave2, wifi, wifi-qcom, wifi-qcom-ac on RouterOS 7

### Features
 * Interfaces: enable/disable, SFP info, PoE-Out control & power monitoring, RX/TX traffic, device presence
 * NAT / Mangle / Filter / Simple Queue rule switches
 * PPP user monitoring and control
 * Kid Control
 * Client traffic monitoring (Accounting on v6, Kid Control Devices on v7+)
 * Device tracker for all network hosts
 * System sensors (CPU, Memory, HDD, Temperature, Voltage, Fan speed)
 * RouterOS and firmware update sensors
 * Script execution
 * Environment variables
 * GPS and UPS monitoring
 * Configurable scan interval and traffic units

## Links
- [Documentation](https://github.com/jnctech/homeassistant-mikrotik_router/tree/master)
- [Configuration](https://github.com/jnctech/homeassistant-mikrotik_router/tree/master#setup-integration)
- [Report a Bug](https://github.com/jnctech/homeassistant-mikrotik_router/issues/new?labels=bug&template=bug_report.md&title=%5BBug%5D)
- [Suggest an idea](https://github.com/jnctech/homeassistant-mikrotik_router/issues/new?labels=enhancement&template=feature_request.md&title=%5BFeature%5D)
- [Upstream repo](https://github.com/tomaae/homeassistant-mikrotik_router) (original by tomaae)
