"""Unit tests for Mikrotik Router entity _skip_sensor() and MikrotikInterfaceEntityMixin."""

from unittest.mock import MagicMock


from custom_components.mikrotik_router.entity import (
    copy_attrs,
    _skip_sensor,
    MikrotikInterfaceEntityMixin,
)
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


def test_skip_poe_measurement_sensor_when_value_is_none():
    """PoE measurement sensors are skipped when API returns None (passive PoE hardware).

    Passive PoE ports (e.g. hAP ax3 ether1) report poe-out-status but the
    measurement fields are absent from the API response and default to None.
    """
    desc = make_entity_desc(data_attribute="poe-out-voltage")
    data = {
        "ether1": {
            "type": "ether",
            "poe-out": "auto-on",
            "poe-out-status": "powered-on",
            "poe-out-voltage": None,
            "poe-out-current": None,
            "poe-out-power": None,
        }
    }
    cfg = make_config_entry({CONF_SENSOR_POE: True})

    assert _skip_sensor(cfg, desc, data, "ether1") is True


def test_no_skip_poe_measurement_sensor_when_hardware_reports_values():
    """PoE measurement sensors are shown when hardware returns real values (CRS, etc.)."""
    desc = make_entity_desc(data_attribute="poe-out-voltage")
    data = {
        "ether1": {
            "type": "ether",
            "poe-out": "auto-on",
            "poe-out-status": "powered-on",
            "poe-out-voltage": 23.8,
            "poe-out-current": 180,
            "poe-out-power": 4.3,
        }
    }
    cfg = make_config_entry({CONF_SENSOR_POE: True})

    assert _skip_sensor(cfg, desc, data, "ether1") is False


# ---------------------------------------------------------------------------
# Client traffic test
# ---------------------------------------------------------------------------


def test_skip_client_traffic_when_attribute_missing():
    """Client traffic sensor is skipped when attribute is not in the data entry."""
    desc = make_entity_desc(data_path="client_traffic", data_attribute="tx-rx-bytes")
    data = {"aa:bb:cc:dd:ee:ff": {"mac-address": "aa:bb:cc:dd:ee:ff"}}
    cfg = make_config_entry()

    assert _skip_sensor(cfg, desc, data, "aa:bb:cc:dd:ee:ff") is True


def test_skip_poe_sensor_when_uid_absent_from_data():
    """PoE sensor is skipped when uid is not present in the data dict at all.

    Guards against KeyError introduced in the PoE uid-not-in-data fix.
    """
    desc = make_entity_desc(data_attribute="poe-out-status")
    data = {}  # uid not present
    cfg = make_config_entry({CONF_SENSOR_POE: True})

    assert _skip_sensor(cfg, desc, data, "ether1") is True


# ---------------------------------------------------------------------------
# MikrotikInterfaceEntityMixin tests
# ---------------------------------------------------------------------------


class _BaseSpy:
    """Minimal base that simulates the HA base-class extra_state_attributes."""

    @property
    def extra_state_attributes(self):
        return {"attribution": "Mikrotik"}


class _ConcreteEntity(MikrotikInterfaceEntityMixin, _BaseSpy):
    """Concrete entity used to exercise the mixin without a real coordinator."""

    def __init__(self, data):
        self._data = data


def test_mixin_ether_adds_ether_attributes():
    """Ether-type interface populates ether-specific attributes."""
    entity = _ConcreteEntity({"type": "ether", "status": "link-ok", "rate": "1Gbps"})
    attrs = entity.extra_state_attributes
    assert "status" in attrs
    assert attrs["status"] == "link-ok"
    assert "rate" in attrs
    assert attrs["rate"] == "1Gbps"


def test_mixin_ether_skips_missing_ether_keys():
    """Only attributes actually present in _data are included."""
    entity = _ConcreteEntity({"type": "ether"})
    attrs = entity.extra_state_attributes
    # DEVICE_ATTRIBUTES_IFACE_ETHER keys should be absent when not in _data
    assert "status" not in attrs
    assert "auto_negotiation" not in attrs


def test_mixin_ether_with_sfp_adds_sfp_attributes():
    """SFP attributes are added for ether interfaces that expose sfp-shutdown-temperature."""
    entity = _ConcreteEntity(
        {
            "type": "ether",
            "sfp-shutdown-temperature": "95C",
            "sfp-temperature": "45C",
            "sfp-vendor-name": "ACME",
        }
    )
    attrs = entity.extra_state_attributes
    assert "sfp_temperature" in attrs
    assert attrs["sfp_temperature"] == "45C"
    assert "sfp_vendor_name" in attrs


def test_mixin_ether_without_sfp_does_not_add_sfp_attributes():
    """SFP attributes are omitted when sfp-shutdown-temperature is absent."""
    entity = _ConcreteEntity(
        {"type": "ether", "status": "link-ok", "sfp-temperature": "45C"}
    )
    attrs = entity.extra_state_attributes
    # sfp-temperature present in data but sfp-shutdown-temperature is not → SFP block skipped
    assert "sfp_temperature" not in attrs


def test_mixin_wlan_adds_wireless_attributes():
    """Wlan-type interface populates wireless-specific attributes."""
    entity = _ConcreteEntity({"type": "wlan", "ssid": "MyWifi", "band": "2ghz-b/g/n"})
    attrs = entity.extra_state_attributes
    assert "ssid" in attrs
    assert attrs["ssid"] == "MyWifi"
    assert "band" in attrs


def test_mixin_other_type_adds_no_extra_attributes():
    """Non-ether/wlan interfaces (e.g. bridge) produce no extra attributes."""
    entity = _ConcreteEntity({"type": "bridge", "status": "active"})
    attrs = entity.extra_state_attributes
    assert "status" not in attrs
    # Only the base attribution key is present
    assert list(attrs.keys()) == ["attribution"]


def test_mixin_missing_type_adds_no_extra_attributes():
    """Missing 'type' key is treated the same as an unrecognised type."""
    entity = _ConcreteEntity({"status": "active"})
    attrs = entity.extra_state_attributes
    assert "status" not in attrs
    assert list(attrs.keys()) == ["attribution"]


def test_mixin_preserves_base_attributes():
    """Mixin does not overwrite attributes returned by the base class."""
    entity = _ConcreteEntity({"type": "ether", "status": "link-ok"})
    attrs = entity.extra_state_attributes
    assert attrs["attribution"] == "Mikrotik"


# ---------------------------------------------------------------------------
# copy_attrs tests
# ---------------------------------------------------------------------------


def testcopy_attrs_copies_existing_keys():
    """Copies matching variables from data to attributes."""
    attributes = {}
    data = {"status": "up", "rate": "1Gbps", "unused": "value"}
    copy_attrs(attributes, data, ["status", "rate"])
    assert "status" in attributes
    assert "rate" in attributes
    assert "unused" not in attributes


def testcopy_attrs_skips_missing_keys():
    """Missing keys in data are skipped without error."""
    attributes = {}
    data = {"status": "up"}
    copy_attrs(attributes, data, ["status", "missing-key"])
    assert "status" in attributes
    assert len(attributes) == 1


def testcopy_attrs_empty_variables_list():
    """Empty variables list copies nothing."""
    attributes = {}
    data = {"status": "up"}
    copy_attrs(attributes, data, [])
    assert len(attributes) == 0


# ---------------------------------------------------------------------------
# Client traffic skip tests
# ---------------------------------------------------------------------------


def test_no_skip_client_traffic_when_attribute_present():
    """Client traffic sensor allowed when attribute exists in data entry."""
    desc = make_entity_desc(data_path="client_traffic", data_attribute="wan-tx")
    data = {"aa:bb:cc:dd:ee:ff": {"wan-tx": 100}}
    cfg = make_config_entry()
    assert _skip_sensor(cfg, desc, data, "aa:bb:cc:dd:ee:ff") is False


# ---------------------------------------------------------------------------
# Host tracker allowed test
# ---------------------------------------------------------------------------


def test_no_skip_host_tracker_when_enabled():
    """Host device tracker allowed when CONF_TRACK_HOSTS is True."""
    desc = make_entity_desc(
        func="MikrotikHostDeviceTracker",
        data_attribute="available",
    )
    data = {"aa:bb:cc:dd:ee:ff": {"available": True}}
    cfg = make_config_entry({CONF_TRACK_HOSTS: True})
    assert _skip_sensor(cfg, desc, data, "aa:bb:cc:dd:ee:ff") is False


# ---------------------------------------------------------------------------
# Netwatch allowed test
# ---------------------------------------------------------------------------


def test_no_skip_netwatch_when_enabled():
    """Netwatch sensor allowed when CONF_SENSOR_NETWATCH_TRACKER is True."""
    desc = make_entity_desc(
        data_path="netwatch",
        data_attribute="status",
    )
    data = {"8.8.8.8": {"status": "up"}}
    cfg = make_config_entry({CONF_SENSOR_NETWATCH_TRACKER: True})
    assert _skip_sensor(cfg, desc, data, "8.8.8.8") is False
