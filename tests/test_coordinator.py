"""Unit tests for Mikrotik Router coordinator and apiparser logic."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from custom_components.mikrotik_router.apiparser import (
    parse_api,
    utc_from_timestamp as apiparser_utc_from_timestamp,
)
from custom_components.mikrotik_router.coordinator import (
    MikrotikCoordinator,
    as_local,
    utc_from_timestamp,
)
from custom_components.mikrotik_router.const import (
    CONF_SCAN_INTERVAL,
    CONF_SENSOR_POE,
    CONF_SENSOR_PORT_TRAFFIC,
    DEFAULT_SENSOR_POE,
    DEFAULT_SENSOR_PORT_TRAFFIC,
)

from .conftest import MockMikrotikAPI

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_coordinator(options=None, api_responses=None, major_fw_version=6):
    """Build a minimal MikrotikCoordinator without triggering __init__."""
    coordinator = object.__new__(MikrotikCoordinator)

    coordinator.ds = {
        "access": ["write", "policy", "reboot", "test"],
        "routerboard": {},
        "resource": {},
        "health": {},
        "health7": {},
        "interface": {},
        "bonding": {},
        "bonding_slaves": {},
        "bridge": {},
        "bridge_host": {},
        "arp": {},
        "nat": {},
        "kid-control": {},
        "mangle": {},
        "filter": {},
        "ppp_secret": {},
        "ppp_active": {},
        "fw-update": {},
        "script": {},
        "queue": {},
        "dns": {},
        "dhcp-server": {},
        "dhcp-client": {},
        "dhcp-network": {},
        "dhcp": {},
        "capsman_hosts": {},
        "wireless": {},
        "wireless_hosts": {},
        "host": {},
        "host_hass": {},
        "hostspot_host": {},
        "client_traffic": {},
        "environment": {},
        "ups": {},
        "gps": {},
        "netwatch": {},
    }

    coordinator.major_fw_version = major_fw_version
    coordinator.minor_fw_version = 0
    coordinator.api = MockMikrotikAPI(responses=api_responses or {})

    cfg = MagicMock()
    cfg.options = options or {}
    coordinator.config_entry = cfg

    return coordinator


# ---------------------------------------------------------------------------
# Group A: parse_api() — pure function tests
# ---------------------------------------------------------------------------


def test_parse_api_no_source_returns_data_unchanged():
    """parse_api with no source and empty vals returns data as-is."""
    data = {"existing": "value"}
    result = parse_api(data=data, source=None, vals=[])
    assert result == {"existing": "value"}


def test_parse_api_no_source_fills_defaults():
    """parse_api with no source and no key fills defaults into data dict."""
    data = {}
    result = parse_api(
        data=data,
        source=None,
        vals=[
            {"name": "temperature", "default": 0},
            {"name": "voltage", "default": 0},
        ],
    )
    assert result["temperature"] == 0
    assert result["voltage"] == 0


def test_parse_api_key_creates_keyed_entry():
    """parse_api with key= creates a keyed entry from source list."""
    data = {}
    source = [{"name": "ether1", "type": "ether", "mac-address": "AA:BB:CC:DD:EE:FF"}]
    result = parse_api(
        data=data,
        source=source,
        key="name",
        vals=[
            {"name": "name"},
            {"name": "type", "default": "unknown"},
        ],
    )
    assert "ether1" in result
    assert result["ether1"]["type"] == "ether"


def test_parse_api_key_search_merges_into_existing_entry():
    """parse_api with key_search= merges data into existing entry by name lookup."""
    data = {
        "uid-abc": {
            "name": "ether1",
            "type": "ether",
            "poe-out": "auto-on",
        }
    }
    source = [
        {
            "name": "ether1",
            "poe-out-status": "powered-on",
            "poe-out-voltage": 24.2,
            "poe-out-current": 0.5,
            "poe-out-power": 12.1,
        }
    ]
    result = parse_api(
        data=data,
        source=source,
        key_search="name",
        vals=[
            {"name": "poe-out-status", "default": "unknown"},
            {"name": "poe-out-voltage", "default": 0},
            {"name": "poe-out-current", "default": 0},
            {"name": "poe-out-power", "default": 0},
        ],
    )
    assert result["uid-abc"]["poe-out-status"] == "powered-on"
    assert result["uid-abc"]["poe-out-voltage"] == pytest.approx(24.2)
    assert result["uid-abc"]["poe-out-current"] == pytest.approx(0.5)
    assert result["uid-abc"]["poe-out-power"] == pytest.approx(12.1)


def test_parse_api_default_used_when_field_missing():
    """parse_api uses default value when a field is absent from source entry."""
    data = {}
    source = [{"name": "ether1"}]
    result = parse_api(
        data=data,
        source=source,
        key="name",
        vals=[
            {"name": "name"},
            {"name": "poe-out", "default": "N/A"},
        ],
    )
    assert result["ether1"]["poe-out"] == "N/A"


def test_parse_api_ensure_vals_adds_missing_keys():
    """parse_api ensure_vals adds keys not present in the existing data."""
    data = {}
    source = [{"name": "ether1", "type": "ether"}]
    result = parse_api(
        data=data,
        source=source,
        key="name",
        vals=[{"name": "name"}, {"name": "type"}],
        ensure_vals=[
            {"name": "rx-previous", "default": 0.0},
            {"name": "tx-previous", "default": 0.0},
        ],
    )
    assert result["ether1"]["rx-previous"] == pytest.approx(0.0)
    assert result["ether1"]["tx-previous"] == pytest.approx(0.0)


def test_parse_api_skip_filters_entries():
    """parse_api skip= skips entries matching skip conditions."""
    data = {}
    source = [
        {"name": "ether1", "type": "ether"},
        {"name": "bridge1", "type": "bridge"},
    ]
    result = parse_api(
        data=data,
        source=source,
        key="name",
        vals=[{"name": "name"}, {"name": "type"}],
        skip=[{"name": "type", "value": "bridge"}],
    )
    assert "ether1" in result
    assert "bridge1" not in result


# ---------------------------------------------------------------------------
# Group B: get_system_health()
# ---------------------------------------------------------------------------


def test_health_access_check_blocks_when_missing_write():
    """get_system_health returns early (no API call) when 'write' not in access."""
    coordinator = make_coordinator(major_fw_version=6)
    coordinator.ds["access"] = ["read", "policy"]
    coordinator.ds["health"] = {}

    coordinator.get_system_health()

    assert coordinator.ds["health"] == {}


def test_health_fw6_populates_poe_in_keys():
    """FW v6: health response with poe-in fields is merged into ds['health']."""
    coordinator = make_coordinator(
        major_fw_version=6,
        api_responses={
            "/system/health": [
                {
                    "temperature": 45,
                    "voltage": 12.0,
                    "poe-in-voltage": 48.1,
                    "poe-in-current": 220,
                }
            ]
        },
    )

    coordinator.get_system_health()

    assert coordinator.ds["health"]["poe-in-voltage"] == pytest.approx(48.1)
    assert coordinator.ds["health"]["poe-in-current"] == 220
    assert coordinator.ds["health"]["temperature"] == 45


def test_health_fw6_missing_poe_in_uses_defaults():
    """FW v6: health response without poe-in fields uses default 0."""
    coordinator = make_coordinator(
        major_fw_version=6,
        api_responses={
            "/system/health": [
                {
                    "temperature": 55,
                    "voltage": 12.1,
                }
            ]
        },
    )

    coordinator.get_system_health()

    assert coordinator.ds["health"]["poe-in-voltage"] == 0
    assert coordinator.ds["health"]["poe-in-current"] == 0


def test_health_fw7_flattens_name_value_pairs():
    """FW v7: name/value pair format is flattened into ds['health']."""
    coordinator = make_coordinator(
        major_fw_version=7,
        api_responses={
            "/system/health": [
                {"name": "temperature", "value": 50},
                {"name": "voltage", "value": 12.1},
                {"name": "poe-in-voltage", "value": 48.0},
            ]
        },
    )

    coordinator.get_system_health()

    assert coordinator.ds["health"]["temperature"] == 50
    assert coordinator.ds["health"]["voltage"] == pytest.approx(12.1)
    assert coordinator.ds["health"]["poe-in-voltage"] == pytest.approx(48.0)


# ---------------------------------------------------------------------------
# Group C: option_sensor_poe property + PoE parse_api merge
# ---------------------------------------------------------------------------


def test_option_sensor_poe_true_when_enabled():
    """option_sensor_poe returns True when CONF_SENSOR_POE is set in options."""
    coordinator = make_coordinator(options={CONF_SENSOR_POE: True})
    assert coordinator.option_sensor_poe is True


def test_option_sensor_poe_false_when_disabled():
    """option_sensor_poe returns False when CONF_SENSOR_POE is False."""
    coordinator = make_coordinator(options={CONF_SENSOR_POE: False})
    assert coordinator.option_sensor_poe is False


def test_option_sensor_poe_default_when_not_set():
    """option_sensor_poe uses DEFAULT_SENSOR_POE when option not in config."""
    coordinator = make_coordinator(options={})
    assert coordinator.option_sensor_poe == DEFAULT_SENSOR_POE


def test_poe_monitor_merges_all_four_fields():
    """parse_api with PoE monitor source merges all 4 poe-out fields into interface."""
    data = {
        "ether1": {
            "name": "ether1",
            "type": "ether",
            "poe-out": "auto-on",
        }
    }
    source = [
        {
            "name": "ether1",
            "poe-out-status": "powered-on",
            "poe-out-voltage": 24.5,
            "poe-out-current": 310,
            "poe-out-power": 7.6,
        }
    ]
    result = parse_api(
        data=data,
        source=source,
        key_search="name",
        vals=[
            {"name": "poe-out-status", "default": "unknown"},
            {"name": "poe-out-voltage", "default": 0},
            {"name": "poe-out-current", "default": 0},
            {"name": "poe-out-power", "default": 0},
        ],
    )
    assert result["ether1"]["poe-out-status"] == "powered-on"
    assert result["ether1"]["poe-out-voltage"] == pytest.approx(24.5)
    assert result["ether1"]["poe-out-current"] == 310
    assert result["ether1"]["poe-out-power"] == pytest.approx(7.6)


def test_poe_monitor_uses_none_defaults_for_missing_fields():
    """parse_api with partial PoE monitor response uses None defaults for missing fields.

    This mirrors the real coordinator behaviour: if the hardware doesn't return
    poe-out-voltage/current/power, they default to None so _skip_sensor() can
    hide those sensors on passive-PoE hardware (e.g. hAP ax3).
    """
    data = {
        "ether1": {
            "name": "ether1",
            "type": "ether",
            "poe-out": "auto-on",
        }
    }
    source = [{"name": "ether1", "poe-out-status": "waiting-for-load"}]
    result = parse_api(
        data=data,
        source=source,
        key_search="name",
        vals=[
            {"name": "poe-out-status", "default": "unknown"},
            {"name": "poe-out-voltage", "default": None},
            {"name": "poe-out-current", "default": None},
            {"name": "poe-out-power", "default": None},
        ],
    )
    assert result["ether1"]["poe-out-status"] == "waiting-for-load"
    assert result["ether1"]["poe-out-voltage"] is None
    assert result["ether1"]["poe-out-current"] is None
    assert result["ether1"]["poe-out-power"] is None


# ---------------------------------------------------------------------------
# Group D: async_process_host() — wired client availability
# ---------------------------------------------------------------------------


def make_coordinator_for_host(arp_entries=None, dhcp_entries=None, host_entries=None):
    """Build a coordinator pre-configured for async_process_host() testing."""
    coordinator = make_coordinator()

    # Required attributes for async_process_host
    coordinator.support_capsman = False
    coordinator.support_wireless = False
    # option_sensor_client_captive is a @property reading from config_entry.options;
    # make_coordinator() sets options={} so it defaults to DEFAULT_SENSOR_CLIENT_CAPTIVE=False
    coordinator.host_hass_recovered = True  # skip HA registry recovery

    mac_lookup = MagicMock()
    mac_lookup.lookup = MagicMock(return_value="Vendor")
    coordinator.async_mac_lookup = mac_lookup

    coordinator.ds["arp"] = arp_entries or {}
    coordinator.ds["dhcp"] = dhcp_entries or {}
    coordinator.ds["host"] = host_entries or {}
    coordinator.ds["resource"] = {"clients_wired": 0, "clients_wireless": 0}
    coordinator.ds["capsman_hosts"] = {}
    coordinator.ds["wireless_hosts"] = {}
    coordinator.ds["dns"] = {}
    coordinator.ds["hostspot_host"] = {}

    return coordinator


@pytest.mark.asyncio
async def test_arp_host_becomes_available():
    """ARP host present in current ARP table is marked available=True."""
    coordinator = make_coordinator_for_host(
        arp_entries={
            "AA:BB:CC:DD:EE:01": {
                "mac-address": "AA:BB:CC:DD:EE:01",
                "address": "192.168.1.10",
                "interface": "ether1",
            }
        }
    )

    await coordinator.async_process_host()

    host = coordinator.ds["host"]["AA:BB:CC:DD:EE:01"]
    assert host["available"] is True
    assert host["last-seen"] is not False


@pytest.mark.asyncio
async def test_arp_host_becomes_unavailable_when_not_in_arp():
    """ARP host previously tracked but absent from current ARP table is unavailable."""
    coordinator = make_coordinator_for_host(
        arp_entries={},  # empty — device left the network
        host_entries={
            "AA:BB:CC:DD:EE:02": {
                "source": "arp",
                "mac-address": "AA:BB:CC:DD:EE:02",
                "address": "192.168.1.11",
                "interface": "ether1",
                "host-name": "mypc",
                "manufacturer": "Vendor",
                "last-seen": False,
                "available": True,  # was available before
            }
        },
    )

    await coordinator.async_process_host()

    assert coordinator.ds["host"]["AA:BB:CC:DD:EE:02"]["available"] is False


@pytest.mark.asyncio
async def test_dhcp_host_available_when_in_arp():
    """DHCP-sourced host is available when its MAC appears in the current ARP table."""
    mac = "AA:BB:CC:DD:EE:03"
    coordinator = make_coordinator_for_host(
        arp_entries={
            mac: {
                "mac-address": mac,
                "address": "192.168.1.12",
                "interface": "ether2",
            }
        },
        dhcp_entries={
            mac: {
                "enabled": True,
                "mac-address": mac,
                "address": "192.168.1.12",
                "interface": "ether2",
                "host-name": "laptop",
                "comment": "",
            }
        },
    )

    await coordinator.async_process_host()

    host = coordinator.ds["host"][mac]
    assert host["available"] is True


@pytest.mark.asyncio
async def test_dhcp_host_unavailable_when_not_in_arp():
    """DHCP host with a valid lease but absent from ARP table is unavailable."""
    mac = "AA:BB:CC:DD:EE:04"
    coordinator = make_coordinator_for_host(
        arp_entries={},  # not in ARP
        dhcp_entries={
            mac: {
                "enabled": True,
                "mac-address": mac,
                "address": "192.168.1.13",
                "interface": "ether2",
                "host-name": "phone",
                "comment": "",
            }
        },
    )

    await coordinator.async_process_host()

    host = coordinator.ds["host"][mac]
    assert host["available"] is False


@pytest.mark.asyncio
async def test_clients_wired_count_increments_for_arp_hosts():
    """clients_wired increments once per available ARP host."""
    coordinator = make_coordinator_for_host(
        arp_entries={
            "AA:BB:CC:DD:EE:05": {
                "mac-address": "AA:BB:CC:DD:EE:05",
                "address": "192.168.1.20",
                "interface": "ether1",
            },
            "AA:BB:CC:DD:EE:06": {
                "mac-address": "AA:BB:CC:DD:EE:06",
                "address": "192.168.1.21",
                "interface": "ether1",
            },
        }
    )

    await coordinator.async_process_host()

    assert coordinator.ds["resource"]["clients_wired"] == 2
    assert coordinator.ds["resource"]["clients_wireless"] == 0


@pytest.mark.asyncio
async def test_wireless_host_not_counted_as_wired():
    """Wireless-sourced host is never counted as a wired client."""
    mac = "AA:BB:CC:DD:EE:07"
    coordinator = make_coordinator_for_host(
        host_entries={
            mac: {
                "source": "wireless",
                "mac-address": mac,
                "address": "192.168.1.30",
                "interface": "wlan1",
                "host-name": "tablet",
                "manufacturer": "Vendor",
                "last-seen": False,
                "available": True,
                "signal-strength": -65,
                "tx-ccq": 90,
                "tx-rate": "54Mbps",
                "rx-rate": "54Mbps",
            }
        }
    )
    coordinator.support_wireless = True
    coordinator.ds["wireless_hosts"] = {
        mac: {
            "mac-address": mac,
            "interface": "wlan1",
            "ap": False,
            "signal-strength": -65,
            "tx-ccq": 90,
            "tx-rate": "54Mbps",
            "rx-rate": "54Mbps",
        }
    }

    await coordinator.async_process_host()

    assert coordinator.ds["resource"]["clients_wired"] == 0
    assert coordinator.ds["resource"]["clients_wireless"] == 1


@pytest.mark.asyncio
async def test_arp_failed_status_not_detected_but_host_created():
    """ARP entry with status 'failed' is NOT counted in arp_detected (#17).

    The host entry IS still created (so it appears in the UI as 'away'),
    but it is not marked available.  The failed entry stays in ds['arp']
    so the tracker coordinator can still look up bridge interfaces.
    """
    mac = "AA:BB:CC:DD:EE:F1"
    coordinator = make_coordinator_for_host(
        arp_entries={
            mac: {
                "mac-address": mac,
                "address": "192.168.1.50",
                "interface": "ether1",
                "status": "failed",
                "bridge": "bridge",
            }
        }
    )

    await coordinator.async_process_host()

    # Host entry created (visible in UI) but marked unavailable
    assert mac in coordinator.ds["host"]
    assert coordinator.ds["host"][mac]["available"] is False

    # Failed entry kept in ds["arp"] for bridge lookups
    assert mac in coordinator.ds["arp"]
    assert coordinator.ds["arp"][mac]["bridge"] == "bridge"


@pytest.mark.asyncio
async def test_arp_reachable_status_detected():
    """ARP entry with non-failed status is counted as detected and available."""
    mac = "AA:BB:CC:DD:EE:F2"
    coordinator = make_coordinator_for_host(
        arp_entries={
            mac: {
                "mac-address": mac,
                "address": "192.168.1.51",
                "interface": "ether1",
                "status": "reachable",
            }
        }
    )

    await coordinator.async_process_host()

    assert coordinator.ds["host"][mac]["available"] is True
    assert coordinator.ds["host"][mac]["last-seen"] is not False


@pytest.mark.asyncio
async def test_arp_empty_status_detected():
    """ARP entry with empty/missing status (static entry) is detected and available."""
    mac = "AA:BB:CC:DD:EE:F3"
    coordinator = make_coordinator_for_host(
        arp_entries={
            mac: {
                "mac-address": mac,
                "address": "192.168.1.52",
                "interface": "ether1",
                "status": "",
            }
        }
    )

    await coordinator.async_process_host()

    assert coordinator.ds["host"][mac]["available"] is True


@pytest.mark.asyncio
async def test_mixed_arp_statuses_only_failed_excluded():
    """Only 'failed' ARP entries are excluded from detection; others are detected."""
    mac_ok = "AA:BB:CC:DD:EE:A1"
    mac_failed = "AA:BB:CC:DD:EE:A2"
    coordinator = make_coordinator_for_host(
        arp_entries={
            mac_ok: {
                "mac-address": mac_ok,
                "address": "192.168.1.60",
                "interface": "ether1",
                "status": "stale",
            },
            mac_failed: {
                "mac-address": mac_failed,
                "address": "192.168.1.61",
                "interface": "ether1",
                "status": "failed",
            },
        }
    )

    await coordinator.async_process_host()

    assert coordinator.ds["host"][mac_ok]["available"] is True
    assert coordinator.ds["host"][mac_failed]["available"] is False


# ---------------------------------------------------------------------------
# Group E: bug-fix regression tests
# ---------------------------------------------------------------------------


def test_get_accounting_uid_by_ip_uses_equality_not_identity():
    """_get_accounting_uid_by_ip returns correct MAC using == not 'is'.

    Regression test for the 'is' vs '==' string comparison fix.
    String interning means 'is' works for short literals but fails for
    dynamically built strings — == is always correct.
    """
    coordinator = make_coordinator()
    coordinator.ds["client_traffic"] = {
        "AA:BB:CC:DD:EE:01": {"address": "192.168.1.10"},
        "AA:BB:CC:DD:EE:02": {"address": "192.168.1.20"},
    }

    # Build IP as a non-interned string to ensure 'is' would fail
    target_ip = "192.168.1." + "20"
    result = coordinator._get_accounting_uid_by_ip(target_ip)

    assert result == "AA:BB:CC:DD:EE:02"


@pytest.mark.asyncio
async def test_mac_lookup_cancelled_error_propagates():
    """asyncio.CancelledError from mac lookup is re-raised, not swallowed.

    Regression test for the bare except swallowing CancelledError fix.
    """
    import asyncio

    coordinator = make_coordinator_for_host(
        arp_entries={
            "AA:BB:CC:DD:EE:FF": {
                "mac-address": "AA:BB:CC:DD:EE:FF",
                "address": "192.168.1.99",
                "interface": "ether1",
            }
        }
    )

    async def raise_cancelled(_mac):
        raise asyncio.CancelledError()

    coordinator.async_mac_lookup.lookup = raise_cancelled

    with pytest.raises(asyncio.CancelledError):
        await coordinator.async_process_host()


# ---------------------------------------------------------------------------
# utc_from_timestamp and as_local tests
# ---------------------------------------------------------------------------


def test_utc_from_timestamp_returns_utc_aware_datetime():
    """utc_from_timestamp produces a UTC-aware datetime from a Unix timestamp."""
    result = utc_from_timestamp(0)
    assert result == datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert result.tzinfo is timezone.utc


def test_utc_from_timestamp_apiparser_matches_coordinator():
    """Both apiparser and coordinator produce identical results."""
    ts = 1_700_000_000.0
    assert apiparser_utc_from_timestamp(ts) == utc_from_timestamp(ts)


def test_as_local_returns_naive_datetime_unchanged_when_no_tz_configured():
    """as_local returns naive datetime unchanged when DEFAULT_TIME_ZONE is None."""
    naive = datetime(2024, 1, 15, 12, 0, 0)
    result = as_local(naive)
    assert result == naive


def test_as_local_attaches_utc_to_naive_datetime_when_tz_configured(monkeypatch):
    """as_local attaches UTC tzinfo to naive datetime when DEFAULT_TIME_ZONE is set."""
    import custom_components.mikrotik_router.coordinator as coord_module

    monkeypatch.setattr(coord_module, "DEFAULT_TIME_ZONE", timezone.utc)
    naive = datetime(2024, 1, 15, 12, 0, 0)
    result = as_local(naive)
    assert result.tzinfo is not None


# ---------------------------------------------------------------------------
# Group F: get_arp — ARP table processing and failed entry filtering
# ---------------------------------------------------------------------------


def test_get_arp_keeps_failed_entries_for_bridge_lookups():
    """ARP entries with status 'failed' are kept in ds['arp'] per ADR-001.

    Failed entries are excluded from availability in async_process_host(),
    not in get_arp(). They must remain for bridge-interface resolution.
    """
    coordinator = make_coordinator(
        api_responses={
            "/ip/arp": [
                {
                    "mac-address": "AA:BB:CC:DD:EE:01",
                    "address": "10.0.0.1",
                    "interface": "ether1",
                    "status": "",
                },
                {
                    "mac-address": "AA:BB:CC:DD:EE:02",
                    "address": "10.0.0.2",
                    "interface": "ether1",
                    "status": "failed",
                },
            ]
        }
    )
    coordinator.ds["bridge"] = {}
    coordinator.ds["bridge_host"] = {}
    coordinator.ds["dhcp-client"] = {}
    coordinator.get_arp()
    assert "AA:BB:CC:DD:EE:01" in coordinator.ds["arp"]
    assert "AA:BB:CC:DD:EE:02" in coordinator.ds["arp"]


def test_get_arp_keeps_entries_without_status():
    """ARP entries without a status field (or empty status) should be kept."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/arp": [
                {
                    "mac-address": "AA:BB:CC:DD:EE:01",
                    "address": "10.0.0.1",
                    "interface": "ether1",
                },
            ]
        }
    )
    coordinator.ds["bridge"] = {}
    coordinator.ds["bridge_host"] = {}
    coordinator.ds["dhcp-client"] = {}
    coordinator.get_arp()
    assert "AA:BB:CC:DD:EE:01" in coordinator.ds["arp"]


def test_get_arp_removes_dhcp_client_interfaces():
    """ARP entries on DHCP client interfaces should be excluded."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/arp": [
                {
                    "mac-address": "AA:BB:CC:DD:EE:01",
                    "address": "10.0.0.1",
                    "interface": "ether1-wan",
                    "status": "",
                },
                {
                    "mac-address": "AA:BB:CC:DD:EE:02",
                    "address": "10.0.0.2",
                    "interface": "ether2",
                    "status": "",
                },
            ]
        }
    )
    coordinator.ds["bridge"] = {}
    coordinator.ds["bridge_host"] = {}
    coordinator.ds["dhcp-client"] = {"ether1-wan": {"interface": "ether1-wan"}}
    coordinator.get_arp()
    assert "AA:BB:CC:DD:EE:01" not in coordinator.ds["arp"]
    assert "AA:BB:CC:DD:EE:02" in coordinator.ds["arp"]


def test_get_arp_resolves_bridge_interface():
    """ARP entries on bridge interfaces get bridge field set and real port resolved."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/arp": [
                {
                    "mac-address": "AA:BB:CC:DD:EE:01",
                    "address": "10.0.0.1",
                    "interface": "bridge",
                    "status": "",
                },
            ]
        }
    )
    coordinator.ds["bridge"] = {"bridge": {"name": "bridge"}}
    coordinator.ds["bridge_host"] = {"AA:BB:CC:DD:EE:01": {"interface": "ether3"}}
    coordinator.ds["dhcp-client"] = {}
    coordinator.get_arp()
    entry = coordinator.ds["arp"]["AA:BB:CC:DD:EE:01"]
    assert entry["bridge"] == "bridge"
    assert entry["interface"] == "ether3"


# ---------------------------------------------------------------------------
# Group G: get_dns — static DNS processing
# ---------------------------------------------------------------------------


def test_get_dns_parses_entries():
    """Static DNS entries are parsed with name, address, comment."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/dns/static": [
                {
                    "name": "router.lan",
                    "address": "10.0.0.1",
                    "comment": "Main Router",
                },
            ]
        }
    )
    coordinator.get_dns()
    assert "router.lan" in coordinator.ds["dns"]
    assert coordinator.ds["dns"]["router.lan"]["address"] == "10.0.0.1"
    assert coordinator.ds["dns"]["router.lan"]["comment"] == "Main Router"


def test_get_dns_comment_converted_to_string():
    """DNS comment field is always converted to string."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/dns/static": [
                {"name": "test.lan", "address": "10.0.0.2", "comment": 12345},
            ]
        }
    )
    coordinator.get_dns()
    assert coordinator.ds["dns"]["test.lan"]["comment"] == "12345"


# ---------------------------------------------------------------------------
# Group H: coordinator option properties
# ---------------------------------------------------------------------------


def test_option_sensor_port_traffic_enabled():
    coordinator = make_coordinator(options={CONF_SENSOR_PORT_TRAFFIC: True})
    assert coordinator.option_sensor_port_traffic is True


def test_option_sensor_port_traffic_default():
    coordinator = make_coordinator(options={})
    assert coordinator.option_sensor_port_traffic == DEFAULT_SENSOR_PORT_TRAFFIC


def test_option_sensor_poe_enabled():
    coordinator = make_coordinator(options={CONF_SENSOR_POE: True})
    assert coordinator.option_sensor_poe is True


def test_option_sensor_poe_default():
    coordinator = make_coordinator(options={})
    assert coordinator.option_sensor_poe == DEFAULT_SENSOR_POE


# ---------------------------------------------------------------------------
# Group I: set_value and execute wrappers
# ---------------------------------------------------------------------------


def test_set_value_delegates_to_api():
    """Coordinator.set_value passes through to api.set_value."""
    coordinator = make_coordinator()
    coordinator.api.set_value = MagicMock(return_value=True)
    result = coordinator.set_value("/interface", "name", "ether1", "disabled", True)
    coordinator.api.set_value.assert_called_once_with(
        "/interface", "name", "ether1", "disabled", True
    )
    assert result is True


def test_execute_delegates_to_api():
    """Coordinator.execute passes through to api.execute."""
    coordinator = make_coordinator()
    coordinator.api.execute = MagicMock(return_value=True)
    result = coordinator.execute("/system", "reboot", None, None)
    coordinator.api.execute.assert_called_once_with(
        "/system", "reboot", None, None, None
    )
    assert result is True


# ---------------------------------------------------------------------------
# Group J: get_system_resource() — CPU, memory, uptime, storage
# ---------------------------------------------------------------------------


def test_system_resource_uptime_parsing():
    """Uptime string '1w2d3h4m5s' is parsed to correct epoch seconds."""
    coordinator = make_coordinator(
        api_responses={
            "/system/resource": [
                {
                    "uptime": "1w2d3h4m5s",
                    "cpu-load": 15,
                    "free-memory": 500000,
                    "total-memory": 1000000,
                    "free-hdd-space": 8000000,
                    "total-hdd-space": 16000000,
                    "platform": "MikroTik",
                    "board-name": "RB4011",
                    "version": "7.16.2",
                }
            ]
        }
    )
    coordinator.rebootcheck = 999999
    coordinator.host = "10.0.0.1"
    coordinator.get_system_resource()

    expected = 1 * 604800 + 2 * 86400 + 3 * 3600 + 4 * 60 + 5
    assert coordinator.ds["resource"]["uptime_epoch"] == expected


def test_system_resource_uptime_seconds_only():
    """Uptime '45s' parses correctly."""
    coordinator = make_coordinator(
        api_responses={
            "/system/resource": [
                {
                    "uptime": "45s",
                    "cpu-load": 5,
                    "free-memory": 100,
                    "total-memory": 200,
                    "free-hdd-space": 100,
                    "total-hdd-space": 200,
                }
            ]
        }
    )
    coordinator.rebootcheck = 999999
    coordinator.host = "10.0.0.1"
    coordinator.get_system_resource()
    assert coordinator.ds["resource"]["uptime_epoch"] == 45


def test_system_resource_memory_usage():
    """Memory usage percentage calculated correctly."""
    coordinator = make_coordinator(
        api_responses={
            "/system/resource": [
                {
                    "uptime": "1h",
                    "cpu-load": 10,
                    "free-memory": 256000000,
                    "total-memory": 1024000000,
                    "free-hdd-space": 100,
                    "total-hdd-space": 200,
                }
            ]
        }
    )
    coordinator.rebootcheck = 999999
    coordinator.host = "10.0.0.1"
    coordinator.get_system_resource()
    assert coordinator.ds["resource"]["memory-usage"] == 75


def test_system_resource_zero_memory_returns_unknown():
    """Zero total memory → memory-usage is 'unknown'."""
    coordinator = make_coordinator(
        api_responses={
            "/system/resource": [
                {
                    "uptime": "1m",
                    "cpu-load": 0,
                    "free-memory": 0,
                    "total-memory": 0,
                    "free-hdd-space": 0,
                    "total-hdd-space": 0,
                }
            ]
        }
    )
    coordinator.rebootcheck = 999999
    coordinator.host = "10.0.0.1"
    coordinator.get_system_resource()
    assert coordinator.ds["resource"]["memory-usage"] == "unknown"
    assert coordinator.ds["resource"]["hdd-usage"] == "unknown"


def test_system_resource_hdd_usage():
    """HDD usage percentage calculated correctly."""
    coordinator = make_coordinator(
        api_responses={
            "/system/resource": [
                {
                    "uptime": "1h",
                    "cpu-load": 5,
                    "free-memory": 100,
                    "total-memory": 200,
                    "free-hdd-space": 4000000,
                    "total-hdd-space": 16000000,
                }
            ]
        }
    )
    coordinator.rebootcheck = 999999
    coordinator.host = "10.0.0.1"
    coordinator.get_system_resource()
    assert coordinator.ds["resource"]["hdd-usage"] == 75


def test_system_resource_reboot_detection():
    """When uptime_epoch < rebootcheck, get_firmware_update is called."""
    coordinator = make_coordinator(
        api_responses={
            "/system/resource": [
                {
                    "uptime": "30s",
                    "cpu-load": 5,
                    "free-memory": 100,
                    "total-memory": 200,
                    "free-hdd-space": 100,
                    "total-hdd-space": 200,
                }
            ]
        }
    )
    coordinator.rebootcheck = 99999  # much larger than 30s
    coordinator.host = "10.0.0.1"
    coordinator.get_firmware_update = MagicMock()
    coordinator.get_system_resource()
    coordinator.get_firmware_update.assert_called_once()


def test_system_resource_no_reboot_if_uptime_grows():
    """Normal operation: uptime grows, no reboot detection."""
    coordinator = make_coordinator(
        api_responses={
            "/system/resource": [
                {
                    "uptime": "2h",
                    "cpu-load": 5,
                    "free-memory": 100,
                    "total-memory": 200,
                    "free-hdd-space": 100,
                    "total-hdd-space": 200,
                }
            ]
        }
    )
    coordinator.rebootcheck = 3600  # 1 hour — less than 2h
    coordinator.host = "10.0.0.1"
    coordinator.get_firmware_update = MagicMock()
    coordinator.get_system_resource()
    coordinator.get_firmware_update.assert_not_called()


# ---------------------------------------------------------------------------
# Group K: get_firmware_update() — version parsing, access control
# ---------------------------------------------------------------------------


def test_firmware_update_available():
    """Firmware update detected when status matches."""
    coordinator = make_coordinator(
        api_responses={
            "/system/package/update": [
                {
                    "status": "New version is available",
                    "channel": "stable",
                    "installed-version": "7.16.1",
                    "latest-version": "7.16.2",
                }
            ]
        }
    )
    coordinator.host = "10.0.0.1"
    coordinator.execute = MagicMock()
    coordinator.get_firmware_update()
    assert coordinator.ds["fw-update"]["available"] is True
    assert coordinator.major_fw_version == 7
    assert coordinator.minor_fw_version == 16


def test_firmware_update_not_available():
    """No update when status is different."""
    coordinator = make_coordinator(
        api_responses={
            "/system/package/update": [
                {
                    "status": "System is already up to date",
                    "channel": "stable",
                    "installed-version": "7.16.2",
                    "latest-version": "7.16.2",
                }
            ]
        }
    )
    coordinator.host = "10.0.0.1"
    coordinator.execute = MagicMock()
    coordinator.get_firmware_update()
    assert coordinator.ds["fw-update"]["available"] is False


def test_firmware_update_blocked_without_access():
    """Firmware check skipped if missing write/policy/reboot access."""
    coordinator = make_coordinator(
        api_responses={
            "/system/package/update": [
                {
                    "status": "New version is available",
                    "installed-version": "7.16.2",
                    "latest-version": "7.17.0",
                }
            ]
        }
    )
    coordinator.ds["access"] = ["read"]  # missing write, policy, reboot
    coordinator.host = "10.0.0.1"
    coordinator.execute = MagicMock()
    coordinator.get_firmware_update()
    coordinator.execute.assert_not_called()
    assert coordinator.ds["fw-update"] == {}


def test_firmware_version_parsing_v6():
    """Version string '6.49' parsed as major=6, minor=49."""
    coordinator = make_coordinator(
        api_responses={
            "/system/package/update": [
                {
                    "status": "System is already up to date",
                    "installed-version": "6.49.10",
                    "latest-version": "6.49.10",
                }
            ]
        }
    )
    coordinator.host = "10.0.0.1"
    coordinator.execute = MagicMock()
    coordinator.get_firmware_update()
    assert coordinator.major_fw_version == 6
    assert coordinator.minor_fw_version == 49


# ---------------------------------------------------------------------------
# Group L: get_nat() — NAT rule parsing and deduplication
# ---------------------------------------------------------------------------


def test_nat_basic_rule():
    """Basic dst-nat rule is parsed correctly."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/firewall/nat": [
                {
                    ".id": "*1",
                    "chain": "dstnat",
                    "action": "dst-nat",
                    "protocol": "tcp",
                    "dst-port": "8080",
                    "in-interface": "ether1",
                    "to-addresses": "192.168.1.100",
                    "to-ports": "80",
                    "comment": "Web server",
                    "disabled": False,
                }
            ]
        }
    )
    coordinator.nat_removed = {}
    coordinator.host = "10.0.0.1"
    coordinator.get_nat()
    assert "*1" in coordinator.ds["nat"]
    rule = coordinator.ds["nat"]["*1"]
    assert rule["action"] == "dst-nat"
    assert rule["protocol"] == "tcp"
    assert rule["enabled"] is True
    assert rule["name"] == "tcp:8080"


def test_nat_filters_non_dst_nat():
    """Only dst-nat rules are kept; masquerade is filtered out."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/firewall/nat": [
                {
                    ".id": "*1",
                    "chain": "srcnat",
                    "action": "masquerade",
                    "disabled": False,
                },
                {
                    ".id": "*2",
                    "chain": "dstnat",
                    "action": "dst-nat",
                    "protocol": "tcp",
                    "dst-port": "443",
                    "to-addresses": "192.168.1.1",
                    "to-ports": "443",
                    "disabled": False,
                },
            ]
        }
    )
    coordinator.nat_removed = {}
    coordinator.host = "10.0.0.1"
    coordinator.get_nat()
    assert "*1" not in coordinator.ds["nat"]
    assert "*2" in coordinator.ds["nat"]


def test_nat_duplicate_removal():
    """Duplicate NAT rules (same uniq-id) are both removed."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/firewall/nat": [
                {
                    ".id": "*1",
                    "chain": "dstnat",
                    "action": "dst-nat",
                    "protocol": "tcp",
                    "dst-port": "80",
                    "in-interface": "ether1",
                    "to-addresses": "192.168.1.1",
                    "to-ports": "80",
                    "comment": "Rule A",
                    "disabled": False,
                },
                {
                    ".id": "*2",
                    "chain": "dstnat",
                    "action": "dst-nat",
                    "protocol": "tcp",
                    "dst-port": "80",
                    "in-interface": "ether1",
                    "to-addresses": "192.168.1.1",
                    "to-ports": "80",
                    "comment": "Rule B",
                    "disabled": False,
                },
            ]
        }
    )
    coordinator.nat_removed = {}
    coordinator.host = "10.0.0.1"
    coordinator.get_nat()
    assert len(coordinator.ds["nat"]) == 0


def test_nat_comment_converted_to_string():
    """NAT comment field is always converted to string."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/firewall/nat": [
                {
                    ".id": "*1",
                    "chain": "dstnat",
                    "action": "dst-nat",
                    "protocol": "tcp",
                    "dst-port": "22",
                    "to-addresses": "10.0.0.2",
                    "to-ports": "22",
                    "comment": 12345,
                    "disabled": False,
                }
            ]
        }
    )
    coordinator.nat_removed = {}
    coordinator.host = "10.0.0.1"
    coordinator.get_nat()
    assert coordinator.ds["nat"]["*1"]["comment"] == "12345"


# ---------------------------------------------------------------------------
# Group M: get_mangle() — mangle rule parsing
# ---------------------------------------------------------------------------


def test_mangle_basic_rule():
    """Basic mangle rule is parsed."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/firewall/mangle": [
                {
                    ".id": "*1",
                    "chain": "prerouting",
                    "action": "mark-routing",
                    "protocol": "tcp",
                    "dst-port": "443",
                    "comment": "HTTPS routing",
                    "disabled": False,
                }
            ]
        }
    )
    coordinator.mangle_removed = {}
    coordinator.host = "10.0.0.1"
    coordinator.get_mangle()
    assert "*1" in coordinator.ds["mangle"]
    assert coordinator.ds["mangle"]["*1"]["action"] == "mark-routing"


def test_mangle_skips_dynamic_and_jump():
    """Dynamic rules and 'jump' actions are excluded."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/firewall/mangle": [
                {
                    ".id": "*1",
                    "chain": "prerouting",
                    "action": "jump",
                    "disabled": False,
                },
                {
                    ".id": "*2",
                    "chain": "prerouting",
                    "action": "mark-routing",
                    "dynamic": True,
                    "disabled": False,
                },
                {
                    ".id": "*3",
                    "chain": "prerouting",
                    "action": "mark-routing",
                    "protocol": "udp",
                    "disabled": False,
                },
            ]
        }
    )
    coordinator.mangle_removed = {}
    coordinator.host = "10.0.0.1"
    coordinator.get_mangle()
    assert "*1" not in coordinator.ds["mangle"]
    assert "*2" not in coordinator.ds["mangle"]
    assert "*3" in coordinator.ds["mangle"]


def test_mangle_duplicate_removal():
    """Duplicate mangle rules are both removed."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/firewall/mangle": [
                {
                    ".id": "*1",
                    "chain": "prerouting",
                    "action": "mark-routing",
                    "protocol": "tcp",
                    "dst-port": "80",
                    "disabled": False,
                },
                {
                    ".id": "*2",
                    "chain": "prerouting",
                    "action": "mark-routing",
                    "protocol": "tcp",
                    "dst-port": "80",
                    "disabled": False,
                },
            ]
        }
    )
    coordinator.mangle_removed = {}
    coordinator.host = "10.0.0.1"
    coordinator.get_mangle()
    assert len(coordinator.ds["mangle"]) == 0


# ---------------------------------------------------------------------------
# Group N: get_filter() — filter rule parsing
# ---------------------------------------------------------------------------


def test_filter_basic_rule():
    """Basic filter rule is parsed."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/firewall/filter": [
                {
                    ".id": "*1",
                    "chain": "forward",
                    "action": "drop",
                    "protocol": "tcp",
                    "dst-port": "445",
                    "comment": "Block SMB",
                    "disabled": False,
                }
            ]
        }
    )
    coordinator.filter_removed = {}
    coordinator.host = "10.0.0.1"
    coordinator.get_filter()
    assert "*1" in coordinator.ds["filter"]
    assert coordinator.ds["filter"]["*1"]["action"] == "drop"
    assert coordinator.ds["filter"]["*1"]["enabled"] is True


def test_filter_skips_dynamic_and_jump():
    """Dynamic rules and 'jump' actions are excluded from filter."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/firewall/filter": [
                {
                    ".id": "*1",
                    "chain": "forward",
                    "action": "jump",
                    "disabled": False,
                },
                {
                    ".id": "*2",
                    "chain": "input",
                    "action": "accept",
                    "dynamic": True,
                    "disabled": False,
                },
                {
                    ".id": "*3",
                    "chain": "forward",
                    "action": "accept",
                    "protocol": "icmp",
                    "disabled": False,
                },
            ]
        }
    )
    coordinator.filter_removed = {}
    coordinator.host = "10.0.0.1"
    coordinator.get_filter()
    assert "*1" not in coordinator.ds["filter"]
    assert "*2" not in coordinator.ds["filter"]
    assert "*3" in coordinator.ds["filter"]


def test_filter_duplicate_removal():
    """Duplicate filter rules are both removed."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/firewall/filter": [
                {
                    ".id": "*1",
                    "chain": "forward",
                    "action": "drop",
                    "protocol": "tcp",
                    "dst-port": "445",
                    "disabled": False,
                },
                {
                    ".id": "*2",
                    "chain": "forward",
                    "action": "drop",
                    "protocol": "tcp",
                    "dst-port": "445",
                    "disabled": False,
                },
            ]
        }
    )
    coordinator.filter_removed = {}
    coordinator.host = "10.0.0.1"
    coordinator.get_filter()
    assert len(coordinator.ds["filter"]) == 0


def test_filter_disabled_reversed_default_true():
    """Filter enabled defaults to True when disabled field is absent."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/firewall/filter": [
                {
                    ".id": "*1",
                    "chain": "forward",
                    "action": "accept",
                }
            ]
        }
    )
    coordinator.filter_removed = {}
    coordinator.host = "10.0.0.1"
    coordinator.get_filter()
    assert coordinator.ds["filter"]["*1"]["enabled"] is True


# ---------------------------------------------------------------------------
# Group O: get_interface() — interface discovery & traffic calculation
# ---------------------------------------------------------------------------


def test_interface_basic_parsing():
    """Basic interface entry is parsed with correct fields."""
    coordinator = make_coordinator(
        options={CONF_SENSOR_PORT_TRAFFIC: False},
        api_responses={
            "/interface": [
                {
                    "default-name": "ether1",
                    ".id": "*1",
                    "name": "ether1",
                    "type": "ether",
                    "running": True,
                    "disabled": False,
                    "mac-address": "AA:BB:CC:DD:EE:01",
                    "rx-byte": 1000,
                    "tx-byte": 2000,
                }
            ],
            "/interface/ethernet": [],
        },
    )
    coordinator.get_interface()
    assert "ether1" in coordinator.ds["interface"]
    iface = coordinator.ds["interface"]["ether1"]
    assert iface["type"] == "ether"
    assert iface["enabled"] is True
    assert iface["running"] is True
    assert iface["port-mac-address"] == "AA:BB:CC:DD:EE:01"


def test_interface_bridge_type_skipped():
    """Bridge-type interfaces are excluded."""
    coordinator = make_coordinator(
        options={CONF_SENSOR_PORT_TRAFFIC: False},
        api_responses={
            "/interface": [
                {
                    "default-name": "bridge1",
                    ".id": "*1",
                    "name": "bridge1",
                    "type": "bridge",
                    "disabled": False,
                    "mac-address": "AA:BB:CC:DD:EE:01",
                },
                {
                    "default-name": "ether1",
                    ".id": "*2",
                    "name": "ether1",
                    "type": "ether",
                    "disabled": False,
                    "mac-address": "AA:BB:CC:DD:EE:02",
                },
            ],
            "/interface/ethernet": [],
        },
    )
    coordinator.get_interface()
    assert "bridge1" not in coordinator.ds["interface"]
    assert "ether1" in coordinator.ds["interface"]


def test_interface_traffic_calculation():
    """Traffic delta is calculated per second when enabled."""
    coordinator = make_coordinator(
        options={CONF_SENSOR_PORT_TRAFFIC: True, CONF_SCAN_INTERVAL: 30},
        api_responses={
            "/interface": [
                {
                    "default-name": "ether1",
                    ".id": "*1",
                    "name": "ether1",
                    "type": "ether",
                    "disabled": False,
                    "mac-address": "AA:BB:CC:DD:EE:01",
                    "rx-byte": 6000,
                    "tx-byte": 9000,
                }
            ],
            "/interface/ethernet": [],
        },
    )
    # Seed previous values (must be non-zero; 0.0 is falsy and triggers first-run logic)
    coordinator.ds["interface"]["ether1"] = {
        "rx-previous": 3000.0,
        "tx-previous": 3000.0,
        "rx": 0.0,
        "tx": 0.0,
    }
    coordinator.get_interface()
    iface = coordinator.ds["interface"]["ether1"]
    # (6000 - 3000) / 30 = 100 bytes/s
    assert iface["rx"] == 100
    # (9000 - 3000) / 30 = 200 bytes/s
    assert iface["tx"] == 200
    assert iface["rx-total"] == 6000
    assert iface["tx-total"] == 9000


def test_interface_traffic_first_run_zero_delta():
    """First run with no previous values → delta is 0."""
    coordinator = make_coordinator(
        options={CONF_SENSOR_PORT_TRAFFIC: True, CONF_SCAN_INTERVAL: 30},
        api_responses={
            "/interface": [
                {
                    "default-name": "ether1",
                    ".id": "*1",
                    "name": "ether1",
                    "type": "ether",
                    "disabled": False,
                    "mac-address": "AA:BB:CC:DD:EE:01",
                    "rx-byte": 5000,
                    "tx-byte": 10000,
                }
            ],
            "/interface/ethernet": [],
        },
    )
    coordinator.get_interface()
    iface = coordinator.ds["interface"]["ether1"]
    # First run: previous is 0 → delta is current-0 but previous defaults to current
    # because `previous_tx = vals["tx-previous"] or current_tx`
    assert iface["rx"] == 0
    assert iface["tx"] == 0


def test_interface_virtual_interface_naming():
    """Virtual interface without default-name uses name as key via key_secondary."""
    coordinator = make_coordinator(
        options={CONF_SENSOR_PORT_TRAFFIC: False},
        api_responses={
            "/interface": [
                {
                    ".id": "*1",
                    "name": "vlan100",
                    "type": "vlan",
                    "disabled": False,
                    "mac-address": "AA:BB:CC:DD:EE:01",
                }
            ],
            "/interface/ethernet": [],
        },
    )
    coordinator.get_interface()
    assert "vlan100" in coordinator.ds["interface"]
    iface = coordinator.ds["interface"]["vlan100"]
    assert iface["default-name"] == ""
    assert "vlan100" in iface["port-mac-address"]


def test_interface_bonding_detected():
    """Bonding interfaces populate bonding and bonding_slaves dicts."""
    coordinator = make_coordinator(
        options={CONF_SENSOR_PORT_TRAFFIC: False},
        api_responses={
            "/interface": [
                {
                    "default-name": "ether1",
                    ".id": "*1",
                    "name": "ether1",
                    "type": "ether",
                    "disabled": False,
                    "mac-address": "AA:BB:CC:DD:EE:01",
                },
                {
                    ".id": "*2",
                    "name": "bond1",
                    "type": "bond",
                    "disabled": False,
                    "mac-address": "AA:BB:CC:DD:EE:02",
                },
            ],
            "/interface/ethernet": [],
            "/interface/bonding": [
                {
                    "name": "bond1",
                    "mac-address": "AA:BB:CC:DD:EE:02",
                    "slaves": "ether1,ether2",
                    "mode": "802.3ad",
                }
            ],
        },
    )
    coordinator.get_interface()
    assert "bond1" in coordinator.ds["bonding"]
    assert "ether1" in coordinator.ds["bonding_slaves"]
    assert "ether2" in coordinator.ds["bonding_slaves"]
    assert coordinator.ds["bonding_slaves"]["ether1"]["master"] == "bond1"


# ---------------------------------------------------------------------------
# Group P: get_dhcp() — DHCP lease parsing
# ---------------------------------------------------------------------------


def test_dhcp_basic_lease():
    """Basic DHCP lease is parsed correctly."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/dhcp-server/lease": [
                {
                    "mac-address": "AA:BB:CC:DD:EE:01",
                    "address": "192.168.1.100",
                    "host-name": "desktop-pc",
                    "status": "bound",
                    "server": "dhcp1",
                    "disabled": False,
                }
            ],
            "/ip/dhcp-server": [
                {"name": "dhcp1", "interface": "bridge1"},
            ],
        }
    )
    coordinator.get_dhcp()
    mac = "AA:BB:CC:DD:EE:01"
    assert mac in coordinator.ds["dhcp"]
    lease = coordinator.ds["dhcp"][mac]
    assert lease["address"] == "192.168.1.100"
    assert lease["host-name"] == "desktop-pc"
    assert lease["interface"] == "bridge1"


def test_dhcp_active_address_override():
    """Active address used when different from static address."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/dhcp-server/lease": [
                {
                    "mac-address": "AA:BB:CC:DD:EE:01",
                    "address": "192.168.1.100",
                    "active-address": "192.168.1.200",
                    "host-name": "pc",
                    "server": "dhcp1",
                    "disabled": False,
                }
            ],
            "/ip/dhcp-server": [
                {"name": "dhcp1", "interface": "bridge1"},
            ],
        }
    )
    coordinator.get_dhcp()
    assert coordinator.ds["dhcp"]["AA:BB:CC:DD:EE:01"]["address"] == "192.168.1.200"


def test_dhcp_invalid_ip_set_to_unknown():
    """Invalid IP address in lease → set to 'unknown'."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/dhcp-server/lease": [
                {
                    "mac-address": "AA:BB:CC:DD:EE:01",
                    "address": "not-an-ip",
                    "host-name": "pc",
                    "server": "dhcp1",
                    "disabled": False,
                }
            ],
            "/ip/dhcp-server": [
                {"name": "dhcp1", "interface": "bridge1"},
            ],
        }
    )
    coordinator.get_dhcp()
    assert coordinator.ds["dhcp"]["AA:BB:CC:DD:EE:01"]["address"] == "unknown"


def test_dhcp_active_mac_override():
    """Active MAC updates the mac-address field inside the existing entry."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/dhcp-server/lease": [
                {
                    "mac-address": "AA:BB:CC:DD:EE:01",
                    "active-mac-address": "AA:BB:CC:DD:EE:02",
                    "address": "192.168.1.100",
                    "host-name": "pc",
                    "server": "dhcp1",
                    "disabled": False,
                }
            ],
            "/ip/dhcp-server": [
                {"name": "dhcp1", "interface": "bridge1"},
            ],
        }
    )
    coordinator.get_dhcp()
    # Dict key stays as original mac, but mac-address value is updated
    assert "AA:BB:CC:DD:EE:01" in coordinator.ds["dhcp"]
    assert (
        coordinator.ds["dhcp"]["AA:BB:CC:DD:EE:01"]["mac-address"]
        == "AA:BB:CC:DD:EE:02"
    )


def test_dhcp_interface_from_arp_fallback():
    """Interface resolved from ARP when DHCP server not found."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/dhcp-server/lease": [
                {
                    "mac-address": "AA:BB:CC:DD:EE:01",
                    "address": "192.168.1.100",
                    "host-name": "pc",
                    "server": "unknown-server",
                    "disabled": False,
                }
            ],
            "/ip/dhcp-server": [],
        }
    )
    coordinator.ds["arp"]["AA:BB:CC:DD:EE:01"] = {
        "interface": "ether1",
        "bridge": "unknown",
    }
    coordinator.get_dhcp()
    assert coordinator.ds["dhcp"]["AA:BB:CC:DD:EE:01"]["interface"] == "ether1"


def test_dhcp_interface_from_arp_bridge():
    """Interface resolved from ARP bridge when available."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/dhcp-server/lease": [
                {
                    "mac-address": "AA:BB:CC:DD:EE:01",
                    "address": "192.168.1.100",
                    "host-name": "pc",
                    "server": "unknown-server",
                    "disabled": False,
                }
            ],
            "/ip/dhcp-server": [],
        }
    )
    coordinator.ds["arp"]["AA:BB:CC:DD:EE:01"] = {
        "interface": "ether1",
        "bridge": "bridge1",
    }
    coordinator.get_dhcp()
    assert coordinator.ds["dhcp"]["AA:BB:CC:DD:EE:01"]["interface"] == "bridge1"


def test_dhcp_server_queried_on_demand():
    """DHCP server is queried only when server not in cache."""
    call_count = 0

    coordinator = make_coordinator(
        api_responses={
            "/ip/dhcp-server/lease": [
                {
                    "mac-address": "AA:BB:CC:DD:EE:01",
                    "address": "192.168.1.100",
                    "server": "dhcp1",
                    "disabled": False,
                },
                {
                    "mac-address": "AA:BB:CC:DD:EE:02",
                    "address": "192.168.1.101",
                    "server": "dhcp1",
                    "disabled": False,
                },
            ],
            "/ip/dhcp-server": [
                {"name": "dhcp1", "interface": "bridge1"},
            ],
        }
    )
    original_get_dhcp_server = coordinator.get_dhcp_server

    def counting_get_dhcp_server():
        nonlocal call_count
        call_count += 1
        original_get_dhcp_server()

    coordinator.get_dhcp_server = counting_get_dhcp_server
    coordinator.get_dhcp()
    # Should be called exactly once (first lease triggers it, second reuses cache)
    assert call_count == 1


def test_dhcp_comment_converted_to_string():
    """DHCP comment field is always converted to string."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/dhcp-server/lease": [
                {
                    "mac-address": "AA:BB:CC:DD:EE:01",
                    "address": "192.168.1.100",
                    "server": "dhcp1",
                    "comment": 42,
                    "disabled": False,
                }
            ],
            "/ip/dhcp-server": [
                {"name": "dhcp1", "interface": "bridge1"},
            ],
        }
    )
    coordinator.get_dhcp()
    assert coordinator.ds["dhcp"]["AA:BB:CC:DD:EE:01"]["comment"] == "42"


# ---------------------------------------------------------------------------
# Group Q: get_dhcp_network() — DHCP network / IPv4Network creation
# ---------------------------------------------------------------------------


def test_dhcp_network_creates_ipv4_network():
    """DHCP network creates IPv4Network object from CIDR address."""
    coordinator = make_coordinator(
        api_responses={
            "/ip/dhcp-server/network": [
                {
                    "address": "192.168.1.0/24",
                    "gateway": "192.168.1.1",
                }
            ]
        }
    )
    coordinator.get_dhcp_network()
    from ipaddress import IPv4Network

    net = coordinator.ds["dhcp-network"]["192.168.1.0/24"]
    assert isinstance(net["IPv4Network"], IPv4Network)
    assert str(net["IPv4Network"]) == "192.168.1.0/24"


# ---------------------------------------------------------------------------
# Group R: get_access() — user access rights
# ---------------------------------------------------------------------------


def test_access_rights_parsed():
    """Access rights are extracted from user group policy."""
    coordinator = make_coordinator(
        api_responses={
            "/user": [{"name": "admin", "group": "full"}],
            "/user/group": [{"name": "full", "policy": "write,policy,reboot,test,api"}],
        }
    )
    coordinator.host = "10.0.0.1"
    coordinator.accessrights_reported = False
    cfg = coordinator.config_entry
    cfg.data = {"username": "admin"}
    coordinator.get_access()
    assert "write" in coordinator.ds["access"]
    assert "policy" in coordinator.ds["access"]
    assert "reboot" in coordinator.ds["access"]
