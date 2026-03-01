"""Tests for MikrotikCoordinator - package detection and wireless support.

These tests verify the fixes for:
- upstream #433: Integration crash on routers without wireless package
- Package constant usage and _pkg_enabled helper
"""

from unittest.mock import patch, MagicMock, PropertyMock

import pytest

from custom_components.mikrotik_router.coordinator import (
    MikrotikCoordinator,
    _pkg_enabled,
)
from custom_components.mikrotik_router.const import (
    DOMAIN,
    PKG_PPP,
    PKG_WIRELESS,
    PKG_UPS,
    PKG_GPS,
    WIFI_PACKAGES,
)

# ---------------------------
#   _pkg_enabled helper tests
# ---------------------------


class TestPkgEnabled:
    """Tests for the _pkg_enabled helper function."""

    def test_package_present_and_enabled(self):
        """Package exists and is enabled -> True."""
        packages = {"wireless": {"enabled": True}}
        assert _pkg_enabled(packages, "wireless") is True

    def test_package_present_but_disabled(self):
        """Package exists but is disabled -> False."""
        packages = {"wireless": {"enabled": False}}
        assert _pkg_enabled(packages, "wireless") is False

    def test_package_missing(self):
        """Package not in dict at all -> False."""
        packages = {"ppp": {"enabled": True}}
        assert _pkg_enabled(packages, "wireless") is False

    def test_empty_packages(self):
        """Empty package dict -> False."""
        assert _pkg_enabled({}, "wireless") is False

    def test_all_known_package_names(self):
        """All PKG_* constants work with the helper."""
        packages = {
            "ppp": {"enabled": True},
            "wireless": {"enabled": True},
            "wifiwave2": {"enabled": False},
            "wifi": {"enabled": True},
            "wifi-qcom": {"enabled": True},
            "wifi-qcom-ac": {"enabled": False},
            "ups": {"enabled": True},
            "gps": {"enabled": False},
        }
        assert _pkg_enabled(packages, PKG_PPP) is True
        assert _pkg_enabled(packages, PKG_WIRELESS) is True
        assert _pkg_enabled(packages, "wifiwave2") is False
        assert _pkg_enabled(packages, "wifi") is True
        assert _pkg_enabled(packages, "wifi-qcom") is True
        assert _pkg_enabled(packages, "wifi-qcom-ac") is False
        assert _pkg_enabled(packages, PKG_UPS) is True
        assert _pkg_enabled(packages, PKG_GPS) is False


# ---------------------------
#   Coordinator package detection tests
# ---------------------------


def _make_coordinator(major_fw=7, minor_fw=15):
    """Create a MikrotikCoordinator with mocked internals for testing get_capabilities."""
    with patch.object(MikrotikCoordinator, "__init__", lambda self, *a, **kw: None):
        coord = MikrotikCoordinator.__new__(MikrotikCoordinator)

    # Set the attributes that __init__ would normally set
    coord.support_capsman = False
    coord.support_wireless = False
    coord.support_ppp = False
    coord.support_ups = False
    coord.support_gps = False
    coord._wifimodule = "wireless"
    coord.major_fw_version = major_fw
    coord.minor_fw_version = minor_fw
    coord.host = "192.168.1.1"
    coord.api = MagicMock()
    return coord


def _make_packages(**kwargs):
    """Build a packages dict. Pass pkg_name=True/False for enabled state."""
    return {name: {"enabled": enabled} for name, enabled in kwargs.items()}


class TestGetCapabilitiesV7NoWireless:
    """Fix #433: Routers without wireless package should not crash.

    The upstream bug was that support_wireless was unconditionally set True
    on RouterOS 7+, causing API queries to /interface/wireless on devices
    like RB4011, RB5009, and CCR series that have no wireless hardware.
    """

    def test_no_wireless_package_at_all(self):
        """RB5009 / CCR with no wifi packages -> wireless disabled."""
        coord = _make_coordinator(major_fw=7, minor_fw=15)
        coord.api.query.return_value = []

        with patch(
            "custom_components.mikrotik_router.coordinator.parse_api",
            return_value=_make_packages(routeros=True),
        ):
            coord.get_capabilities()

        assert coord.support_wireless is False
        assert coord.support_capsman is False
        assert coord.support_ppp is True  # v7+ always has ppp

    def test_wireless_package_disabled(self):
        """Wireless package present but disabled -> wireless disabled."""
        coord = _make_coordinator(major_fw=7, minor_fw=15)

        with patch(
            "custom_components.mikrotik_router.coordinator.parse_api",
            return_value=_make_packages(wireless=False),
        ):
            coord.get_capabilities()

        assert coord.support_wireless is False
        assert coord.support_capsman is False

    def test_only_ppp_package(self):
        """Router with only ppp package, no wireless -> no crash."""
        coord = _make_coordinator(major_fw=7, minor_fw=15)

        with patch(
            "custom_components.mikrotik_router.coordinator.parse_api",
            return_value=_make_packages(ppp=True),
        ):
            coord.get_capabilities()

        assert coord.support_wireless is False
        assert coord.support_ppp is True


class TestGetCapabilitiesV7WifiPackages:
    """Verify correct wifi module detection for each RouterOS 7+ package variant."""

    def test_wifiwave2_package(self):
        """Device with wifiwave2 (early WiFi 6) -> module=wifiwave2."""
        coord = _make_coordinator(major_fw=7, minor_fw=10)

        with patch(
            "custom_components.mikrotik_router.coordinator.parse_api",
            return_value=_make_packages(wifiwave2=True),
        ):
            coord.get_capabilities()

        assert coord.support_wireless is True
        assert coord.support_capsman is False
        assert coord._wifimodule == "wifiwave2"

    def test_wifi_package(self):
        """Device with wifi package (RouterOS 7.13+) -> module=wifi."""
        coord = _make_coordinator(major_fw=7, minor_fw=15)

        with patch(
            "custom_components.mikrotik_router.coordinator.parse_api",
            return_value=_make_packages(wifi=True),
        ):
            coord.get_capabilities()

        assert coord.support_wireless is True
        assert coord.support_capsman is False
        assert coord._wifimodule == "wifi"

    def test_wifi_qcom_package(self):
        """Device with wifi-qcom (Qualcomm chipset) -> module=wifi."""
        coord = _make_coordinator(major_fw=7, minor_fw=15)

        with patch(
            "custom_components.mikrotik_router.coordinator.parse_api",
            return_value=_make_packages(**{"wifi-qcom": True}),
        ):
            coord.get_capabilities()

        assert coord.support_wireless is True
        assert coord._wifimodule == "wifi"

    def test_wifi_qcom_ac_package(self):
        """Device with wifi-qcom-ac (Qualcomm AC chipset) -> module=wifi."""
        coord = _make_coordinator(major_fw=7, minor_fw=15)

        with patch(
            "custom_components.mikrotik_router.coordinator.parse_api",
            return_value=_make_packages(**{"wifi-qcom-ac": True}),
        ):
            coord.get_capabilities()

        assert coord.support_wireless is True
        assert coord._wifimodule == "wifi"

    def test_legacy_wireless_on_v7(self):
        """Device with legacy wireless package on v7 -> capsman + wireless."""
        coord = _make_coordinator(major_fw=7, minor_fw=10)

        with patch(
            "custom_components.mikrotik_router.coordinator.parse_api",
            return_value=_make_packages(wireless=True),
        ):
            coord.get_capabilities()

        assert coord.support_wireless is True
        assert coord.support_capsman is True
        assert coord._wifimodule == "wireless"

    def test_wifiwave2_takes_priority_over_wireless(self):
        """When both wifiwave2 and wireless exist, wifiwave2 wins."""
        coord = _make_coordinator(major_fw=7, minor_fw=10)

        with patch(
            "custom_components.mikrotik_router.coordinator.parse_api",
            return_value=_make_packages(wifiwave2=True, wireless=True),
        ):
            coord.get_capabilities()

        assert coord.support_wireless is True
        assert coord.support_capsman is False  # modern wifi, no capsman
        assert coord._wifimodule == "wifiwave2"

    def test_wifi_packages_priority_order(self):
        """WIFI_PACKAGES defines the correct priority order."""
        # Verify the constant itself
        pkg_names = [name for name, _ in WIFI_PACKAGES]
        assert pkg_names == ["wifiwave2", "wifi", "wifi-qcom", "wifi-qcom-ac"]


class TestGetCapabilitiesV6:
    """Verify v6 (pre-7) package detection still works correctly."""

    def test_v6_wireless_enabled(self):
        """RouterOS 6 with wireless package enabled."""
        coord = _make_coordinator(major_fw=6, minor_fw=49)

        with patch(
            "custom_components.mikrotik_router.coordinator.parse_api",
            return_value=_make_packages(ppp=True, wireless=True),
        ):
            coord.get_capabilities()

        assert coord.support_wireless is True
        assert coord.support_capsman is True
        assert coord.support_ppp is True

    def test_v6_wireless_disabled(self):
        """RouterOS 6 with wireless package disabled."""
        coord = _make_coordinator(major_fw=6, minor_fw=49)

        with patch(
            "custom_components.mikrotik_router.coordinator.parse_api",
            return_value=_make_packages(ppp=True, wireless=False),
        ):
            coord.get_capabilities()

        assert coord.support_wireless is False
        assert coord.support_capsman is False
        assert coord.support_ppp is True

    def test_v6_no_wireless_package(self):
        """RouterOS 6 with no wireless package at all."""
        coord = _make_coordinator(major_fw=6, minor_fw=49)

        with patch(
            "custom_components.mikrotik_router.coordinator.parse_api",
            return_value=_make_packages(ppp=True),
        ):
            coord.get_capabilities()

        assert coord.support_wireless is False
        assert coord.support_capsman is False


class TestGetCapabilitiesUpsGps:
    """UPS and GPS package detection (all firmware versions)."""

    def test_ups_enabled(self):
        """UPS package present and enabled."""
        coord = _make_coordinator(major_fw=7, minor_fw=15)

        with patch(
            "custom_components.mikrotik_router.coordinator.parse_api",
            return_value=_make_packages(ups=True),
        ):
            coord.get_capabilities()

        assert coord.support_ups is True
        assert coord.support_gps is False

    def test_gps_enabled(self):
        """GPS package present and enabled."""
        coord = _make_coordinator(major_fw=7, minor_fw=15)

        with patch(
            "custom_components.mikrotik_router.coordinator.parse_api",
            return_value=_make_packages(gps=True),
        ):
            coord.get_capabilities()

        assert coord.support_gps is True
        assert coord.support_ups is False

    def test_ups_disabled(self):
        """UPS package present but disabled -> not supported."""
        coord = _make_coordinator(major_fw=7, minor_fw=15)

        with patch(
            "custom_components.mikrotik_router.coordinator.parse_api",
            return_value=_make_packages(ups=False),
        ):
            coord.get_capabilities()

        assert coord.support_ups is False
