# Sensor Gap Analysis — MikroTik Router HACS Integration

**Date:** 2026-03-25
**Branch:** `claude/sensor-gap-analysis-GGBIz`
**Status:** Draft for review — no code changes

---

## 1. Executive Summary

The integration currently surfaces **~44 sensor entities, 4 binary sensors, 10 switch types, 1 button type, 1 device tracker type, and 2 update entities** across 6 platforms. It queries **~33 RouterOS API endpoints**.

This analysis identifies **3 categories of gaps**:
- **Category A** — Data already fetched but not surfaced as entities (low effort)
- **Category B** — RouterOS API endpoints not queried, high home-automation value (medium effort)
- **Category C** — RouterOS API endpoints not queried, niche/advanced use (higher effort)

---

## 2. Category A — Already Fetched, Not Surfaced

These items are the lowest-hanging fruit. The data is already in `self.ds` and just needs entity definitions in `*_types.py`.

| # | Data Point | Source in `self.ds` | Proposed Entity | Platform | Effort | HA Value |
|---|-----------|---------------------|-----------------|----------|--------|----------|
| A1 | Firewall rule byte/packet counters | `nat`, `filter`, `mangle`, `raw` | Per-rule traffic counter sensor | sensor | Low | Medium — see which rules are active |
| A2 | Interface `tx-queue-drop` | `interface` | Queue drops per interface | sensor | Low | Medium — detect congestion |
| A3 | Interface `link-downs` count | `interface` | Link flap counter | sensor | Low | High — detect unstable links |
| A4 | DHCP lease `status` | `dhcp` | Lease status (bound/waiting) | sensor | Low | Low |
| A5 | DHCP lease count | `dhcp` | Total active DHCP leases | sensor | Low | Medium — network utilization |
| A6 | DNS static entry count | `dns` | DNS entries count | sensor | Low | Low |
| A7 | ARP table size | `arp` | ARP entries count | sensor | Low | Medium — detect network scans |
| A8 | Queue actual rate (download/upload) | `queue` | Current throughput per queue | sensor | Low | High — bandwidth monitoring |
| A9 | Wireless client signal strength | `wireless_hosts` | Per-client signal quality | sensor | Low | High — WiFi health monitoring |
| A10 | Wireless client TX/RX rate | `wireless_hosts` | Per-client link rate | sensor | Low | High — WiFi performance |
| A11 | Container status | `container` | Container running state | binary_sensor | Low | High — service monitoring |
| A12 | Bridge host count | `bridge_host` | Devices per bridge | sensor | Low | Low |
| A13 | PPP active connection details | `ppp_active` | PPP caller-id, encoding, address | sensor attr | Low | Medium — VPN user tracking |
| A14 | Resource `platform` / `board-name` | `resource` | Diagnostic sensor | sensor | Low | Low — already in device info |
| A15 | Hotspot authorized/bypassed counts | `hostspot_host` (sic) | Captive portal stats | sensor | Low | Medium |

**Estimated total effort for Category A:** 2-3 days (mostly boilerplate `*_types.py` entries)

---

## 3. Category B — Not Fetched, High Home-Automation Value

These require new API calls in the coordinator plus entity definitions. Prioritized by alignment with typical home automation use cases.

| # | RouterOS API Path | Proposed Entities | Platform | Effort | HA Value | Rationale |
|---|------------------|-------------------|----------|--------|----------|-----------|
| B1 | `/ip/firewall/address-list` | Address list entries (enable/disable) | switch + sensor | Medium | **Very High** | Widely used for ad-blocking, geo-blocking, parental control, dynamic allow/deny lists. Users frequently toggle these from HA. |
| B2 | `/interface/wireguard` + `/interface/wireguard/peers` | WireGuard tunnel status, peer connected, last handshake, TX/RX, endpoint | binary_sensor + sensor | Medium | **Very High** | WireGuard is the dominant VPN for home users. Presence detection via VPN, remote access monitoring. |
| B3 | `/ip/neighbor` (MNDP/CDP/LLDP) | Neighbor device discovery | sensor | Medium | **High** | Network topology awareness, detect new devices on network, identify switches/APs. |
| B4 | `/ip/route` | Active route count, default gateway status, specific route monitoring | sensor + binary_sensor | Medium | **High** | Failover detection, multi-WAN monitoring, route availability. |
| B5 | `/ip/address` | IP addresses per interface | sensor | Low-Med | **High** | Track WAN IP changes, interface addressing, useful for DDNS-like automations. |
| B6 | `/system/scheduler` | Scheduled task status, next-run, run-count | sensor | Low-Med | **Medium** | Monitor cron-like tasks, detect missed runs. |
| B7 | `/ip/cloud` | DDNS hostname, status, public IP | sensor | Low | **High** | Dynamic DNS monitoring, external IP detection without third-party service. |
| B8 | `/system/ntp/client` | NTP sync status, offset, last adjustment | binary_sensor + sensor | Low | **Medium** | Time accuracy monitoring for security-sensitive setups. |
| B9 | `/certificate` | Certificate name, expiry date, days until expiry | sensor | Low-Med | **High** | TLS certificate expiry alerts — critical for HTTPS services, VPN, hotspot. |
| B10 | `/interface/lte` | LTE signal (RSSI, RSRP, RSRQ, SINR), carrier, connection status | sensor + binary_sensor | Medium | **Very High** | LTE failover monitoring is a top request for rural/backup internet users. But only relevant if router has LTE. |
| B11 | `/ip/firewall/connection` (tracking summary) | Active connection count, TCP/UDP/ICMP counts | sensor | Low-Med | **High** | Network activity monitoring, detect anomalies, connection table saturation. |
| B12 | `/interface/pppoe-client` | PPPoE connection status, uptime, IP assigned | binary_sensor + sensor | Low-Med | **High** | Many ISPs use PPPoE — connection monitoring and failover. |
| B13 | `/ip/service` | Service enabled status (winbox, ssh, www, api, ftp) | binary_sensor | Low | **Medium** | Security monitoring — alert if unexpected services enabled. |
| B14 | `/ip/pool` | Pool name, used/total addresses | sensor | Low | **Medium** | DHCP pool exhaustion detection. |
| B15 | `/log` (last N entries) | Recent log entries | sensor | Medium | **Medium** | Surfacing critical router events (login failures, interface down, etc.) into HA. High noise risk. |
| B16 | `/interface/bridge` + `/interface/bridge/port` | Bridge STP status, port roles, path cost | sensor | Low-Med | **Low-Med** | STP topology change detection. Niche but useful for larger setups. |
| B17 | `/interface/vlan` | VLAN interface info | sensor | Low | **Low** | Mostly informational — VLANs are already interfaces. |

**Estimated total effort for Category B:** 3-5 weeks (depending on scope selected)

---

## 4. Category C — Not Fetched, Niche/Advanced

Lower priority items for specialized use cases.

| # | RouterOS API Path | Proposed Entities | Effort | HA Value | Notes |
|---|------------------|-------------------|--------|----------|-------|
| C1 | `/ip/ipsec/active-peers` + `/ip/ipsec/installed-sa` | IPsec tunnel status | Medium | Medium | Site-to-site VPN monitoring |
| C2 | `/routing/ospf/neighbor` | OSPF neighbor status | Medium | Low | Enterprise routing, very niche for HA |
| C3 | `/routing/bgp/session` | BGP session status | Medium | Low | Enterprise, very niche |
| C4 | `/ipv6/address` | IPv6 addresses | Low | Low-Med | Growing relevance as IPv6 adoption increases |
| C5 | `/ipv6/firewall/filter` | IPv6 firewall rules | Medium | Low | Mirror of IPv4 firewall |
| C6 | `/disk` | Disk name, size, free, type | Low | Low | ROS7 only, most routers have minimal storage |
| C7 | `/snmp` | SNMP status | Low | Low | Informational only |
| C8 | `/ip/proxy` | Web proxy stats | Low | Low | Rarely used in home setups |
| C9 | `/system/license` | License level, deadline | Low | Low | Informational |
| C10 | `/interface/ovpn-server` + `/interface/sstp-server` | OpenVPN/SSTP server connections | Medium | Medium | Being replaced by WireGuard |
| C11 | `/tool/torch` (live traffic) | Real-time per-protocol traffic | High | Medium | Very high API load, not suited for polling |
| C12 | `/ip/dns/cache` | DNS cache size, entries | Low | Low | Informational only |
| C13 | `/system/history` | Command audit log | Low | Low-Med | Security audit trail |

---

## 5. Recommended Implementation Priority

### Phase 1 — Quick Wins (Category A, ~2-3 days)
Items that add value with minimal risk since the data is already collected:

1. **A3** — Interface link-downs counter (network reliability)
2. **A8** — Queue actual rates (bandwidth visibility)
3. **A9/A10** — Wireless client signal/rate (WiFi monitoring)
4. **A11** — Container running binary_sensor
5. **A1** — Firewall rule counters
6. **A5** — DHCP lease count
7. **A2** — Queue drops per interface

### Phase 2 — High-Value New Data (Category B, ~2-3 weeks)
New API calls with the highest home-automation alignment:

1. **B1** — Address list management (extremely popular use case)
2. **B2** — WireGuard VPN monitoring (modern VPN standard)
3. **B5** — IP address tracking (WAN IP change detection)
4. **B7** — Cloud/DDNS status (external IP without third-party)
5. **B4** — Route monitoring (failover detection)
6. **B11** — Connection tracking stats (activity monitoring)

### Phase 3 — Conditional/Hardware-Specific (Category B, ~1-2 weeks)
Only relevant for specific hardware:

1. **B10** — LTE modem stats (if hardware present)
2. **B12** — PPPoE client status (if ISP uses PPPoE)
3. **B9** — Certificate expiry monitoring
4. **B13** — Service status (security hardening)

### Phase 4 — Nice to Have
Cherry-pick from remaining Category B and C items based on user demand.

---

## 6. Implementation Complexity Notes

### Adding a Category A sensor (template)
1. Add entry to `sensor_types.py` (or appropriate `*_types.py`)
2. Ensure `data_path` and `data_attribute` match existing `self.ds` keys
3. Add to sensor list filter in `sensor.py` if needed
4. Write tests
5. **No coordinator changes needed**

### Adding a Category B sensor (template)
1. Add new API query method in `coordinator.py` (e.g., `get_wireguard()`)
2. Initialize `self.ds["wireguard"]` in coordinator `__init__`
3. Add call to `_async_update_data()` loop
4. Optionally gate behind capability check (like wireless/container)
5. Add entity descriptions in `*_types.py`
6. Add entity class if custom logic needed (or reuse existing)
7. Write tests for both coordinator method and entity
8. **Coordinator changes required — higher review bar**

### Performance Considerations
- Each new API call adds ~50-200ms to the polling cycle (currently 30s)
- Category A items add **zero** polling overhead
- Category B items should be gated behind capability detection (e.g., don't query WireGuard if not installed)
- Some endpoints (like `/log`, `/ip/firewall/connection`) can return large datasets — need pagination or filtering
- Consider making new data sources opt-in via config flow options

### Breaking Change Risk
- Category A: **None** — additive only
- Category B: **None** — new entities, no changes to existing
- No ADR required unless changing entity identity patterns or data formats

---

## 7. Comparison with Other Router Integrations

For context, here's what comparable HA integrations surface:

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

*Signal data is fetched and available as device_tracker attribute, but not as a dedicated sensor entity.

---

## 8. Decision Required

Before implementation:
1. **Scope** — Which phases/items to include in first PR?
2. **Opt-in vs auto-discover** — Should new sensors be enabled by default or require config flow opt-in?
3. **Polling impact** — Accept increased polling time for Category B, or make them configurable poll intervals?
4. **Entity naming** — Follow existing naming conventions or take opportunity to align with HA 2024+ entity naming standards?

---

## Appendix: Currently Surfaced Entities (Complete List)

<details>
<summary>Click to expand full current entity list</summary>

### Sensors (44)
- System: temperature, voltage, cpu-temperature, switch-temperature, board-temperature1, phy-temperature, power-consumption, poe-out-consumption, poe-in-voltage, poe-in-current, fan1-4 speed, psu1-2 current/voltage
- Resources: uptime, cpu-load, memory-usage, hdd-usage, clients-wired, clients-wireless, captive-authorized
- PoE ports: poe-out-status, poe-out-voltage, poe-out-current, poe-out-power
- Interface traffic: tx, rx, tx-total, rx-total (per interface)
- Client traffic: lan-tx, lan-rx, wan-tx, wan-rx, tx, rx (per client)
- GPS: latitude, longitude
- Environment: value
- DHCP client: status, address

### Binary Sensors (4)
- UPS on-line status
- PPP secret connected
- Interface running
- Netwatch status

### Switches (10 types)
- Interface enable/disable
- NAT rule enable/disable
- Mangle rule enable/disable
- Filter rule enable/disable
- RAW rule enable/disable
- PPP secret enable/disable
- Queue enable/disable
- Kid control enable/disable
- Kid control pause/resume
- Container start/stop

### Buttons (1)
- Script execution

### Device Trackers (1)
- Host connection status

### Update Entities (2)
- RouterOS update
- RouterBOARD firmware update

</details>
