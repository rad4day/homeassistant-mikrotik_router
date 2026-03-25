# Sensor Gap Analysis — MikroTik Router HACS Integration

This document catalogues RouterOS data points that could be surfaced as Home Assistant entities. Items are grouped by whether the data is already fetched by the coordinator or requires new API calls.

---

## Data Already Fetched — Not Yet Surfaced

The coordinator already queries these from RouterOS. Surfacing them as entities requires only new definitions in `*_types.py`.

| Data Point | Source | Proposed Entity | Use Case |
|-----------|--------|-----------------|----------|
| Firewall rule byte/packet counters | `nat`, `filter`, `mangle`, `raw` | Per-rule traffic counter | See which rules are active |
| Interface `tx-queue-drop` | `interface` | Queue drops per interface | Detect congestion |
| Interface `link-downs` count | `interface` | Link flap counter | Detect unstable links |
| DHCP lease `status` | `dhcp` | Lease status (bound/waiting) | Lease monitoring |
| DHCP lease count | `dhcp` | Total active leases | Network utilisation |
| DNS static entry count | `dns` | DNS entries count | Informational |
| ARP table size | `arp` | ARP entries count | Detect network scans |
| Queue actual rate | `queue` | Current throughput per queue | Bandwidth monitoring |
| Wireless client signal strength | `wireless_hosts` | Per-client signal quality | WiFi health |
| Wireless client TX/RX rate | `wireless_hosts` | Per-client link rate | WiFi performance |
| Container status | `container` | Container running state | Service monitoring |
| Bridge host count | `bridge_host` | Devices per bridge | Informational |
| PPP active connection details | `ppp_active` | Caller-id, encoding, address | VPN user tracking |
| Hotspot authorised/bypassed counts | `hostspot_host` | Captive portal stats | Hotspot monitoring |

---

## New API Calls — High Home-Automation Value

These require new RouterOS API queries in the coordinator. Ordered by relevance to typical home automation setups.

| RouterOS API | Proposed Entities | Use Case |
|-------------|-------------------|----------|
| `/ip/firewall/address-list` | Address list entries (enable/disable) | Ad-blocking, geo-blocking, parental control, dynamic allow/deny lists |
| `/interface/wireguard` + `/interface/wireguard/peers` | Tunnel status, peer connected, last handshake, TX/RX | VPN presence detection, remote access monitoring |
| `/ip/neighbor` (MNDP/CDP/LLDP) | Neighbour device discovery | Network topology awareness, detect new devices |
| `/ip/route` | Active route count, default gateway status | Failover detection, multi-WAN monitoring |
| `/ip/address` | IP addresses per interface | WAN IP change detection, DDNS-like automations |
| `/ip/cloud` | DDNS hostname, status, public IP | External IP detection without third-party service |
| `/system/scheduler` | Task status, next-run, run-count | Monitor scheduled tasks, detect missed runs |
| `/system/ntp/client` | NTP sync status, offset | Time accuracy monitoring |
| `/certificate` | Certificate name, expiry date, days until expiry | TLS certificate expiry alerts for HTTPS, VPN, hotspot |
| `/interface/lte` | Signal (RSSI, RSRP, RSRQ, SINR), carrier, status | LTE failover monitoring (hardware-dependent) |
| `/ip/firewall/connection` | Active connection count, TCP/UDP/ICMP | Network activity monitoring, connection table saturation |
| `/interface/pppoe-client` | Connection status, uptime, IP assigned | PPPoE ISP connection monitoring |
| `/ip/service` | Service enabled status (winbox, ssh, www, api, ftp) | Security monitoring — alert on unexpected services |
| `/ip/pool` | Pool name, used/total addresses | DHCP pool exhaustion detection |
| `/log` (last N entries) | Recent log entries | Router event surfacing (login failures, interface down) |
| `/interface/bridge` + `/interface/bridge/port` | STP status, port roles | Topology change detection |

---

## New API Calls — Niche / Advanced

Specialised use cases — lower priority for typical home setups.

| RouterOS API | Proposed Entities | Use Case |
|-------------|-------------------|----------|
| `/ip/ipsec/active-peers` + `/ip/ipsec/installed-sa` | IPsec tunnel status | Site-to-site VPN monitoring |
| `/routing/ospf/neighbor` | OSPF neighbour status | Enterprise dynamic routing |
| `/routing/bgp/session` | BGP session status | Enterprise / multi-homing |
| `/ipv6/address` | IPv6 addresses | IPv6 network monitoring |
| `/ipv6/firewall/filter` | IPv6 firewall rules | Mirror of IPv4 firewall for dual-stack |
| `/disk` | Disk name, size, free, type | Storage monitoring (ROS7 only) |
| `/interface/ovpn-server` + `/interface/sstp-server` | OpenVPN/SSTP connections | Legacy VPN monitoring |
| `/tool/torch` | Real-time per-protocol traffic | Live traffic analysis (high API load) |
| `/ip/dns/cache` | DNS cache size | Informational |
| `/system/history` | Command audit log | Security audit trail |
| `/system/license` | Licence level, deadline | Informational |

---

## Comparison with Other Router Integrations

| Feature | This Integration | UniFi | Fritz!Box | OpenWrt |
|---------|-----------------|-------|-----------|---------|
| System health (CPU/mem/temp) | ✅ | ✅ | ✅ | ✅ |
| Interface traffic | ✅ | ✅ | ✅ | ✅ |
| Per-client traffic | ✅ | ✅ | ❌ | ❌ |
| Device tracker | ✅ | ✅ | ✅ | ✅ |
| Firewall rule control | ✅ | ❌ | ❌ | ❌ |
| VPN status (WireGuard) | ❌ | ✅ | ✅ | ✅ |
| Address list management | ❌ | N/A | N/A | ❌ |
| WAN IP monitoring | ❌ | ✅ | ✅ | ✅ |
| LTE modem stats | ❌ | N/A | ✅ | ✅ |
| Certificate expiry | ❌ | ❌ | ❌ | ❌ |
| Connection count | ❌ | ✅ | ✅ | ❌ |
| PoE management | ✅ | ✅ | N/A | N/A |
| Container management | ✅ | N/A | N/A | ✅ |
| WiFi signal per client | ❌* | ✅ | ✅ | ✅ |
| DDNS/Cloud status | ❌ | ✅ | ✅ | ✅ |

*Signal data is available as a device tracker attribute but not as a dedicated sensor entity.

---

## Current Entity Summary

<details>
<summary>Click to expand</summary>

### Sensors
- **System:** temperature, voltage, cpu-temperature, switch-temperature, board-temperature1, phy-temperature, power-consumption, poe-out-consumption, poe-in-voltage, poe-in-current, fan1-4 speed, psu1-2 current/voltage
- **Resources:** uptime, cpu-load, memory-usage, hdd-usage, clients-wired, clients-wireless, captive-authorised
- **PoE ports:** poe-out-status, poe-out-voltage, poe-out-current, poe-out-power
- **Interface traffic:** tx, rx, tx-total, rx-total (per interface)
- **Client traffic:** lan-tx, lan-rx, wan-tx, wan-rx, tx, rx (per client)
- **GPS:** latitude, longitude
- **Environment:** value
- **DHCP client:** status, address

### Binary Sensors
- UPS on-line status, PPP secret connected, interface running, netwatch status

### Switches (10 types)
- Interface, NAT, mangle, filter, RAW, PPP secret, queue, kid control, kid control pause, container

### Other
- Script execution (button), host connection status (device tracker), RouterOS update, RouterBOARD firmware update

</details>
