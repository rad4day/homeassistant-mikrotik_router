"""Unit tests for Mikrotik Router coordinator and apiparser logic."""

from unittest.mock import MagicMock

import pytest

from custom_components.mikrotik_router.apiparser import parse_api
from custom_components.mikrotik_router.coordinator import MikrotikCoordinator
from custom_components.mikrotik_router.const import (
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
    assert result["uid-abc"]["poe-out-voltage"] == 24.2
    assert result["uid-abc"]["poe-out-current"] == 0.5
    assert result["uid-abc"]["poe-out-power"] == 12.1


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
    assert result["ether1"]["rx-previous"] == 0.0
    assert result["ether1"]["tx-previous"] == 0.0


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

    assert coordinator.ds["health"]["poe-in-voltage"] == 48.1
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
    assert coordinator.ds["health"]["voltage"] == 12.1
    assert coordinator.ds["health"]["poe-in-voltage"] == 48.0


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
    assert result["ether1"]["poe-out-voltage"] == 24.5
    assert result["ether1"]["poe-out-current"] == 310
    assert result["ether1"]["poe-out-power"] == 7.6


def test_poe_monitor_uses_defaults_for_missing_fields():
    """parse_api with partial PoE monitor response uses defaults for missing fields."""
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
            {"name": "poe-out-voltage", "default": 0},
            {"name": "poe-out-current", "default": 0},
            {"name": "poe-out-power", "default": 0},
        ],
    )
    assert result["ether1"]["poe-out-status"] == "waiting-for-load"
    assert result["ether1"]["poe-out-voltage"] == 0
    assert result["ether1"]["poe-out-current"] == 0
    assert result["ether1"]["poe-out-power"] == 0
