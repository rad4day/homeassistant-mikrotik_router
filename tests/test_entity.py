"""Unit tests for Mikrotik Router entity _skip_sensor() logic."""

from unittest.mock import MagicMock

import pytest

from custom_components.mikrotik_router.entity import _skip_sensor
from custom_components.mikrotik_router.const import (
    CONF_SENSOR_PORT_TRAFFIC,
    CONF_SENSOR_PORT_TRACKER,
    CONF_SENSOR_NETWATCH_TRACKER,
    CONF_TRACK_HOSTS,
    CONF_SENSOR_POE,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_entity_desc(**kwargs):
    """Build a minimal entity_description MagicMock with given attributes."""
    desc = MagicMock()
    desc.func = kwargs.get("func", "MikrotikSensor")
    desc.data_path = kwargs.get("data_path", "interface")
    desc.data_attribute = kwargs.get("data_attribute", "tx")
    return desc


def make_config_entry(options=None):
    """Build a mock config_entry with the given options dict."""
    cfg = MagicMock()
    cfg.options = options or {}
    return cfg


# ---------------------------------------------------------------------------
# Traffic sensor tests
# ---------------------------------------------------------------------------


def test_skip_traffic_sensor_when_option_disabled():
    """Traffic sensor is skipped when CONF_SENSOR_PORT_TRAFFIC is False."""
    desc = make_entity_desc(func="MikrotikInterfaceTrafficSensor")
    data = {"ether1": {"type": "ether"}}
    cfg = make_config_entry({CONF_SENSOR_PORT_TRAFFIC: False})

    assert _skip_sensor(cfg, desc, data, "ether1") is True


def test_skip_traffic_sensor_on_bridge_interface():
    """Traffic sensor is skipped for bridge-type interfaces."""
    desc = make_entity_desc(func="MikrotikInterfaceTrafficSensor")
    data = {"bridge1": {"type": "bridge"}}
    cfg = make_config_entry({CONF_SENSOR_PORT_TRAFFIC: True})

    assert _skip_sensor(cfg, desc, data, "bridge1") is True


def test_no_skip_traffic_sensor_on_ether_interface():
    """Traffic sensor is not skipped for ether interfaces when option enabled."""
    desc = make_entity_desc(func="MikrotikInterfaceTrafficSensor")
    data = {"ether1": {"type": "ether"}}
    cfg = make_config_entry({CONF_SENSOR_PORT_TRAFFIC: True})

    assert _skip_sensor(cfg, desc, data, "ether1") is False


# ---------------------------------------------------------------------------
# Port binary sensor tests
# ---------------------------------------------------------------------------


def test_skip_port_binary_sensor_on_wlan_interface():
    """Port binary sensor is skipped for wlan-type interfaces."""
    desc = make_entity_desc(func="MikrotikPortBinarySensor")
    data = {"wlan1": {"type": "wlan"}}
    cfg = make_config_entry({CONF_SENSOR_PORT_TRACKER: True})

    assert _skip_sensor(cfg, desc, data, "wlan1") is True


def test_skip_port_binary_sensor_when_option_disabled():
    """Port binary sensor is skipped when CONF_SENSOR_PORT_TRACKER is False."""
    desc = make_entity_desc(func="MikrotikPortBinarySensor")
    data = {"ether1": {"type": "ether"}}
    cfg = make_config_entry({CONF_SENSOR_PORT_TRACKER: False})

    assert _skip_sensor(cfg, desc, data, "ether1") is True


def test_no_skip_port_binary_sensor_on_ether_when_enabled():
    """Port binary sensor is not skipped for ether interface when option enabled."""
    desc = make_entity_desc(func="MikrotikPortBinarySensor")
    data = {"ether1": {"type": "ether"}}
    cfg = make_config_entry({CONF_SENSOR_PORT_TRACKER: True})

    assert _skip_sensor(cfg, desc, data, "ether1") is False


# ---------------------------------------------------------------------------
# Netwatch + host tracker tests
# ---------------------------------------------------------------------------


def test_skip_netwatch_sensor_when_option_disabled():
    """Netwatch sensor is skipped when CONF_SENSOR_NETWATCH_TRACKER is False."""
    desc = make_entity_desc(data_path="netwatch")
    data = {"8.8.8.8": {"host": "8.8.8.8"}}
    cfg = make_config_entry({CONF_SENSOR_NETWATCH_TRACKER: False})

    assert _skip_sensor(cfg, desc, data, "8.8.8.8") is True


def test_skip_host_tracker_when_option_disabled():
    """Host device tracker is skipped when CONF_TRACK_HOSTS is False."""
    desc = make_entity_desc(func="MikrotikHostDeviceTracker")
    data = {"aa:bb:cc:dd:ee:ff": {"mac-address": "aa:bb:cc:dd:ee:ff"}}
    cfg = make_config_entry({CONF_TRACK_HOSTS: False})

    assert _skip_sensor(cfg, desc, data, "aa:bb:cc:dd:ee:ff") is True


# ---------------------------------------------------------------------------
# PoE sensor tests
# ---------------------------------------------------------------------------


def test_skip_poe_sensor_when_option_disabled():
    """PoE-out sensor is skipped when CONF_SENSOR_POE is False."""
    desc = make_entity_desc(data_attribute="poe-out-status")
    data = {
        "ether1": {
            "type": "ether",
            "poe-out": "auto-on",
            "poe-out-status": "powered-on",
        }
    }
    cfg = make_config_entry({CONF_SENSOR_POE: False})

    assert _skip_sensor(cfg, desc, data, "ether1") is True


def test_skip_poe_sensor_when_interface_not_poe_capable():
    """PoE-out sensor is skipped when poe-out-status is None (non-PoE interface)."""
    desc = make_entity_desc(data_attribute="poe-out-status")
    data = {"ether1": {"type": "ether", "poe-out": "N/A"}}
    cfg = make_config_entry({CONF_SENSOR_POE: True})

    assert _skip_sensor(cfg, desc, data, "ether1") is True


def test_no_skip_poe_sensor_on_poe_capable_interface():
    """PoE-out sensor is not skipped when poe-out-status is set and option enabled."""
    desc = make_entity_desc(data_attribute="poe-out-status")
    data = {
        "ether1": {
            "type": "ether",
            "poe-out": "auto-on",
            "poe-out-status": "powered-on",
        }
    }
    cfg = make_config_entry({CONF_SENSOR_POE: True})

    assert _skip_sensor(cfg, desc, data, "ether1") is False


def test_skip_poe_voltage_sensor_on_non_poe_interface():
    """PoE-out voltage sensor is also skipped on non-PoE interfaces."""
    desc = make_entity_desc(data_attribute="poe-out-voltage")
    data = {"ether1": {"type": "ether"}}
    cfg = make_config_entry({CONF_SENSOR_POE: True})

    assert _skip_sensor(cfg, desc, data, "ether1") is True


# ---------------------------------------------------------------------------
# Client traffic test
# ---------------------------------------------------------------------------


def test_skip_client_traffic_when_attribute_missing():
    """Client traffic sensor is skipped when attribute is not in the data entry."""
    desc = make_entity_desc(data_path="client_traffic", data_attribute="tx-rx-bytes")
    data = {"aa:bb:cc:dd:ee:ff": {"mac-address": "aa:bb:cc:dd:ee:ff"}}
    cfg = make_config_entry()

    assert _skip_sensor(cfg, desc, data, "aa:bb:cc:dd:ee:ff") is True
