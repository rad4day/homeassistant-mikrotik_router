"""Support for the Mikrotik Router switches."""

from __future__ import annotations

from logging import getLogger
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.restore_state import RestoreEntity

from .entity import MikrotikEntity, MikrotikInterfaceEntityMixin, async_add_entities
from .switch_types import (
    SENSOR_TYPES,  # noqa: F401
    SENSOR_SERVICES,  # noqa: F401
)

_LOGGER = getLogger(__name__)

_CAPSMAN_MANAGED = "managed by CAPsMAN"
_RULE_NOT_FOUND_ENABLE = "Rule not found for %s, cannot enable"
_RULE_NOT_FOUND_DISABLE = "Rule not found for %s, cannot disable"


# ---------------------------
#   async_setup_entry
# ---------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    _async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up entry for component"""
    dispatcher = {
        "MikrotikSwitch": MikrotikSwitch,
        "MikrotikPortSwitch": MikrotikPortSwitch,
        "MikrotikNATSwitch": MikrotikNATSwitch,
        "MikrotikMangleSwitch": MikrotikMangleSwitch,
        "MikrotikFilterSwitch": MikrotikFilterSwitch,
        "MikrotikQueueSwitch": MikrotikQueueSwitch,
        "MikrotikRawSwitch": MikrotikRawSwitch,
        "MikrotikContainerSwitch": MikrotikContainerSwitch,
        "MikrotikKidcontrolPauseSwitch": MikrotikKidcontrolPauseSwitch,
    }
    await async_add_entities(hass, config_entry, dispatcher)


# ---------------------------
#   MikrotikSwitch
# ---------------------------
class MikrotikSwitch(MikrotikEntity, SwitchEntity, RestoreEntity):
    """Representation of a switch."""

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        return self._data[self.entity_description.data_attribute]

    @property
    def icon(self) -> str:
        """Return the icon."""
        if self._data[self.entity_description.data_attribute]:
            return self.entity_description.icon_enabled
        else:
            return self.entity_description.icon_disabled

    def _require_write_access(self) -> None:
        """Raise HomeAssistantError if write access is not available."""
        if "write" not in self.coordinator.data["access"]:
            raise HomeAssistantError("Write access required")

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        param = self.entity_description.data_reference
        value = self._data[self.entity_description.data_reference]
        if value is None:
            _LOGGER.error(_RULE_NOT_FOUND_ENABLE, self.entity_id)
            return
        mod_param = self.entity_description.data_switch_parameter
        await self.hass.async_add_executor_job(
            self.coordinator.set_value, path, param, value, mod_param, False
        )
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        param = self.entity_description.data_reference
        value = self._data[self.entity_description.data_reference]
        if value is None:
            _LOGGER.error(_RULE_NOT_FOUND_DISABLE, self.entity_id)
            return
        mod_param = self.entity_description.data_switch_parameter
        await self.hass.async_add_executor_job(
            self.coordinator.set_value, path, param, value, mod_param, True
        )
        await self.coordinator.async_refresh()


# ---------------------------
#   MikrotikPortSwitch
# ---------------------------
class MikrotikPortSwitch(MikrotikInterfaceEntityMixin, MikrotikSwitch):
    """Representation of a network port switch."""

    @property
    def icon(self) -> str:
        """Return the icon."""
        if self._data["running"]:
            icon = self.entity_description.icon_enabled
        else:
            icon = self.entity_description.icon_disabled

        if not self._data["enabled"]:
            icon = "mdi:lan-disconnect"

        return icon

    async def async_turn_on(self, **kwargs: Any) -> str | None:
        """Turn on the switch."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        param = self.entity_description.data_reference
        if self._data.get("about") == _CAPSMAN_MANAGED:
            _LOGGER.error("Unable to enable %s, managed by CAPsMAN", self._data[param])
            return _CAPSMAN_MANAGED
        if "-" in self._data.get("port-mac-address", ""):
            param = "name"
        value = self._data[self.entity_description.data_reference]
        mod_param = self.entity_description.data_switch_parameter
        await self.hass.async_add_executor_job(
            self.coordinator.set_value, path, param, value, mod_param, False
        )

        if "poe-out" in self._data and self._data["poe-out"] == "off":
            path = "/interface/ethernet"
            await self.hass.async_add_executor_job(
                self.coordinator.set_value, path, param, value, "poe-out", "auto-on"
            )

        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> str | None:
        """Turn off the switch."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        param = self.entity_description.data_reference
        if self._data.get("about") == _CAPSMAN_MANAGED:
            _LOGGER.error("Unable to disable %s, managed by CAPsMAN", self._data[param])
            return _CAPSMAN_MANAGED
        if "-" in self._data.get("port-mac-address", ""):
            param = "name"
        value = self._data[self.entity_description.data_reference]
        mod_param = self.entity_description.data_switch_parameter
        await self.hass.async_add_executor_job(
            self.coordinator.set_value, path, param, value, mod_param, True
        )

        if "poe-out" in self._data and self._data["poe-out"] == "auto-on":
            path = "/interface/ethernet"
            await self.hass.async_add_executor_job(
                self.coordinator.set_value, path, param, value, "poe-out", "off"
            )

        await self.coordinator.async_refresh()


# ---------------------------
#   MikrotikNATSwitch
# ---------------------------
class MikrotikNATSwitch(MikrotikSwitch):
    """Representation of a NAT switch."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        param = ".id"
        value = None
        for uid in self.coordinator.data["nat"]:
            if self.coordinator.data["nat"][uid]["uniq-id"] == (
                f"{self._data['chain']},{self._data['action']},{self._data['protocol']},"
                f"{self._data['in-interface']}:{self._data['dst-port']}-"
                f"{self._data['out-interface']}:{self._data['to-addresses']}:{self._data['to-ports']}"
            ):
                value = self.coordinator.data["nat"][uid][".id"]

        if value is None:
            _LOGGER.error(_RULE_NOT_FOUND_ENABLE, self.entity_id)
            return
        mod_param = self.entity_description.data_switch_parameter
        await self.hass.async_add_executor_job(
            self.coordinator.set_value, path, param, value, mod_param, False
        )
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        param = ".id"
        value = None
        for uid in self.coordinator.data["nat"]:
            if self.coordinator.data["nat"][uid]["uniq-id"] == (
                f"{self._data['chain']},{self._data['action']},{self._data['protocol']},"
                f"{self._data['in-interface']}:{self._data['dst-port']}-"
                f"{self._data['out-interface']}:{self._data['to-addresses']}:{self._data['to-ports']}"
            ):
                value = self.coordinator.data["nat"][uid][".id"]

        if value is None:
            _LOGGER.error(_RULE_NOT_FOUND_DISABLE, self.entity_id)
            return
        mod_param = self.entity_description.data_switch_parameter
        await self.hass.async_add_executor_job(
            self.coordinator.set_value, path, param, value, mod_param, True
        )
        await self.coordinator.async_refresh()


# ---------------------------
#   MikrotikMangleSwitch
# ---------------------------
class MikrotikMangleSwitch(MikrotikSwitch):
    """Representation of a Mangle switch."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        param = ".id"
        value = None
        for uid in self.coordinator.data["mangle"]:
            if self.coordinator.data["mangle"][uid]["uniq-id"] == (
                f"{self._data['chain']},{self._data['action']},{self._data['protocol']},"
                f"{self._data['src-address']}:{self._data['src-port']}-"
                f"{self._data['dst-address']}:{self._data['dst-port']},"
                f"{self._data['src-address-list']}-{self._data['dst-address-list']}"
            ):
                value = self.coordinator.data["mangle"][uid][".id"]

        if value is None:
            _LOGGER.error(_RULE_NOT_FOUND_ENABLE, self.entity_id)
            return
        mod_param = self.entity_description.data_switch_parameter
        await self.hass.async_add_executor_job(
            self.coordinator.set_value, path, param, value, mod_param, False
        )
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        param = ".id"
        value = None
        for uid in self.coordinator.data["mangle"]:
            if self.coordinator.data["mangle"][uid]["uniq-id"] == (
                f"{self._data['chain']},{self._data['action']},{self._data['protocol']},"
                f"{self._data['src-address']}:{self._data['src-port']}-"
                f"{self._data['dst-address']}:{self._data['dst-port']},"
                f"{self._data['src-address-list']}-{self._data['dst-address-list']}"
            ):
                value = self.coordinator.data["mangle"][uid][".id"]

        if value is None:
            _LOGGER.error(_RULE_NOT_FOUND_DISABLE, self.entity_id)
            return
        mod_param = self.entity_description.data_switch_parameter
        await self.hass.async_add_executor_job(
            self.coordinator.set_value, path, param, value, mod_param, True
        )
        await self.coordinator.async_refresh()


# ---------------------------
#   MikrotikFilterSwitch
# ---------------------------
class MikrotikFilterSwitch(MikrotikSwitch):
    """Representation of a Filter switch."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        param = ".id"
        value = None
        for uid in self.coordinator.data["filter"]:
            if self.coordinator.data["filter"][uid]["uniq-id"] == (
                f"{self._data['chain']},{self._data['action']},{self._data['protocol']},{self._data['layer7-protocol']},"
                f"{self._data['in-interface']},{self._data['in-interface-list']}:{self._data['src-address']},{self._data['src-address-list']}:{self._data['src-port']}-"
                f"{self._data['out-interface']},{self._data['out-interface-list']}:{self._data['dst-address']},{self._data['dst-address-list']}:{self._data['dst-port']}"
            ):
                value = self.coordinator.data["filter"][uid][".id"]

        if value is None:
            _LOGGER.error(_RULE_NOT_FOUND_ENABLE, self.entity_id)
            return
        mod_param = self.entity_description.data_switch_parameter
        await self.hass.async_add_executor_job(
            self.coordinator.set_value, path, param, value, mod_param, False
        )
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        param = ".id"
        value = None
        for uid in self.coordinator.data["filter"]:
            if self.coordinator.data["filter"][uid]["uniq-id"] == (
                f"{self._data['chain']},{self._data['action']},{self._data['protocol']},{self._data['layer7-protocol']},"
                f"{self._data['in-interface']},{self._data['in-interface-list']}:{self._data['src-address']},{self._data['src-address-list']}:{self._data['src-port']}-"
                f"{self._data['out-interface']},{self._data['out-interface-list']}:{self._data['dst-address']},{self._data['dst-address-list']}:{self._data['dst-port']}"
            ):
                value = self.coordinator.data["filter"][uid][".id"]

        if value is None:
            _LOGGER.error(_RULE_NOT_FOUND_DISABLE, self.entity_id)
            return
        mod_param = self.entity_description.data_switch_parameter
        await self.hass.async_add_executor_job(
            self.coordinator.set_value, path, param, value, mod_param, True
        )
        await self.coordinator.async_refresh()


# ---------------------------
#   MikrotikQueueSwitch
# ---------------------------
class MikrotikQueueSwitch(MikrotikSwitch):
    """Representation of a queue switch."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        param = ".id"
        value = None
        for uid in self.coordinator.data["queue"]:
            if self.coordinator.data["queue"][uid]["name"] == f"{self._data['name']}":
                value = self.coordinator.data["queue"][uid][".id"]

        if value is None:
            _LOGGER.error(_RULE_NOT_FOUND_ENABLE, self.entity_id)
            return
        mod_param = self.entity_description.data_switch_parameter
        await self.hass.async_add_executor_job(
            self.coordinator.set_value, path, param, value, mod_param, False
        )
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        param = ".id"
        value = None
        for uid in self.coordinator.data["queue"]:
            if self.coordinator.data["queue"][uid]["name"] == f"{self._data['name']}":
                value = self.coordinator.data["queue"][uid][".id"]

        if value is None:
            _LOGGER.error(_RULE_NOT_FOUND_DISABLE, self.entity_id)
            return
        mod_param = self.entity_description.data_switch_parameter
        await self.hass.async_add_executor_job(
            self.coordinator.set_value, path, param, value, mod_param, True
        )
        await self.coordinator.async_refresh()


# ---------------------------
#   MikrotikKidcontrolPauseSwitch
# ---------------------------
class MikrotikKidcontrolPauseSwitch(MikrotikSwitch):
    """Representation of a queue switch."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        param = self.entity_description.data_reference
        value = self._data[self.entity_description.data_reference]
        command = "resume"
        await self.hass.async_add_executor_job(
            self.coordinator.execute, path, command, param, value
        )
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        param = self.entity_description.data_reference
        value = self._data[self.entity_description.data_reference]
        command = "pause"
        await self.hass.async_add_executor_job(
            self.coordinator.execute, path, command, param, value
        )
        await self.coordinator.async_refresh()


# ---------------------------
#   MikrotikRawSwitch
# ---------------------------
class MikrotikRawSwitch(MikrotikSwitch):
    """Representation of a Firewall RAW switch."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        param = ".id"
        value = None
        for uid in self.coordinator.data["raw"]:
            if self.coordinator.data["raw"][uid]["uniq-id"] == (
                f"{self._data['chain']},{self._data['action']},{self._data['protocol']},"
                f"{self._data['in-interface']},{self._data['in-interface-list']}:"
                f"{self._data['src-address']},{self._data['src-address-list']}:{self._data['src-port']}-"
                f"{self._data['out-interface']},{self._data['out-interface-list']}:"
                f"{self._data['dst-address']},{self._data['dst-address-list']}:{self._data['dst-port']}"
            ):
                value = self.coordinator.data["raw"][uid][".id"]

        if value is None:
            _LOGGER.error(_RULE_NOT_FOUND_ENABLE, self.entity_id)
            return
        mod_param = self.entity_description.data_switch_parameter
        await self.hass.async_add_executor_job(
            self.coordinator.set_value, path, param, value, mod_param, False
        )
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        param = ".id"
        value = None
        for uid in self.coordinator.data["raw"]:
            if self.coordinator.data["raw"][uid]["uniq-id"] == (
                f"{self._data['chain']},{self._data['action']},{self._data['protocol']},"
                f"{self._data['in-interface']},{self._data['in-interface-list']}:"
                f"{self._data['src-address']},{self._data['src-address-list']}:{self._data['src-port']}-"
                f"{self._data['out-interface']},{self._data['out-interface-list']}:"
                f"{self._data['dst-address']},{self._data['dst-address-list']}:{self._data['dst-port']}"
            ):
                value = self.coordinator.data["raw"][uid][".id"]

        if value is None:
            _LOGGER.error(_RULE_NOT_FOUND_DISABLE, self.entity_id)
            return
        mod_param = self.entity_description.data_switch_parameter
        await self.hass.async_add_executor_job(
            self.coordinator.set_value, path, param, value, mod_param, True
        )
        await self.coordinator.async_refresh()


# ---------------------------
#   MikrotikContainerSwitch
# ---------------------------
class MikrotikContainerSwitch(MikrotikSwitch):
    """Representation of a container start/stop switch."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Start the container."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        await self.hass.async_add_executor_job(
            self.coordinator.execute, path, "start", ".id", self._data[".id"]
        )
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Stop the container."""
        self._require_write_access()

        path = self.entity_description.data_switch_path
        await self.hass.async_add_executor_job(
            self.coordinator.execute, path, "stop", ".id", self._data[".id"]
        )
        await self.coordinator.async_refresh()
