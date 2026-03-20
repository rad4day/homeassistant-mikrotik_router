"""Mikrotik HA shared entity model"""

from __future__ import annotations

from collections.abc import Mapping
from logging import getLogger
from typing import Any, Callable, TypeVar

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME, CONF_HOST
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import (
    entity_platform as ep,
    entity_registry as er,
)
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import (
    DOMAIN,
    ATTRIBUTION,
    CONF_SENSOR_PORT_TRAFFIC,
    DEFAULT_SENSOR_PORT_TRAFFIC,
    CONF_TRACK_HOSTS,
    DEFAULT_TRACK_HOSTS,
    CONF_SENSOR_PORT_TRACKER,
    DEFAULT_SENSOR_PORT_TRACKER,
    CONF_SENSOR_NETWATCH_TRACKER,
    DEFAULT_SENSOR_NETWATCH_TRACKER,
    CONF_SENSOR_POE,
    DEFAULT_SENSOR_POE,
)
from .coordinator import MikrotikCoordinator, MikrotikTrackerCoordinator
from .helper import format_attribute
from .iface_attributes import (
    DEVICE_ATTRIBUTES_IFACE_ETHER,
    DEVICE_ATTRIBUTES_IFACE_SFP,
    DEVICE_ATTRIBUTES_IFACE_WIRELESS,
)

_LOGGER = getLogger(__name__)


def _copy_attrs(attributes: dict, data: dict, variables: list) -> None:
    """Copy data values for each variable in the list into attributes."""
    for variable in variables:
        if variable in data:
            attributes[format_attribute(variable)] = data[variable]


class MikrotikInterfaceEntityMixin:
    """Mixin providing interface-type-aware extra state attributes.

    Used by both MikrotikPortBinarySensor and MikrotikInterfaceTrafficSensor
    to avoid duplicating the ether/SFP/wlan attribute logic.
    """

    @property
    def extra_state_attributes(self):
        """Return type-specific interface state attributes."""
        attributes = super().extra_state_attributes

        if self._data.get("type") == "ether":
            _copy_attrs(attributes, self._data, DEVICE_ATTRIBUTES_IFACE_ETHER)
            if "sfp-shutdown-temperature" in self._data:
                _copy_attrs(attributes, self._data, DEVICE_ATTRIBUTES_IFACE_SFP)
        elif self._data.get("type") == "wlan":
            _copy_attrs(attributes, self._data, DEVICE_ATTRIBUTES_IFACE_WIRELESS)

        return attributes


def _skip_sensor(config_entry, entity_description, data, uid) -> bool:
    # Sensors
    if (
        entity_description.func == "MikrotikInterfaceTrafficSensor"
        and not config_entry.options.get(
            CONF_SENSOR_PORT_TRAFFIC, DEFAULT_SENSOR_PORT_TRAFFIC
        )
    ):
        return True

    if (
        entity_description.func == "MikrotikInterfaceTrafficSensor"
        and data[uid]["type"] == "bridge"
    ):
        return True

    if (
        entity_description.data_path == "client_traffic"
        and entity_description.data_attribute not in data[uid].keys()
    ):
        return True

    # Binary sensors
    if (
        entity_description.func == "MikrotikPortBinarySensor"
        and data[uid]["type"] == "wlan"
    ):
        return True

    if (
        entity_description.func == "MikrotikPortBinarySensor"
        and not config_entry.options.get(
            CONF_SENSOR_PORT_TRACKER, DEFAULT_SENSOR_PORT_TRACKER
        )
    ):
        return True

    if entity_description.data_path == "netwatch" and not config_entry.options.get(
        CONF_SENSOR_NETWATCH_TRACKER, DEFAULT_SENSOR_NETWATCH_TRACKER
    ):
        return True

    # Device Tracker
    if (
        # Skip if host tracking is disabled
        entity_description.func == "MikrotikHostDeviceTracker"
        and not config_entry.options.get(CONF_TRACK_HOSTS, DEFAULT_TRACK_HOSTS)
    ):
        return True

    # Skip PoE-out sensors if disabled or interface doesn't support PoE
    if entity_description.data_attribute in (
        "poe-out-status",
        "poe-out-voltage",
        "poe-out-current",
        "poe-out-power",
    ):
        if not config_entry.options.get(CONF_SENSOR_POE, DEFAULT_SENSOR_POE):
            return True
        if uid not in data or data[uid].get("poe-out-status") is None:
            return True
        # Skip measurement sensors on hardware that doesn't report power monitoring
        if (
            entity_description.data_attribute
            in (
                "poe-out-voltage",
                "poe-out-current",
                "poe-out-power",
            )
            and data[uid].get(entity_description.data_attribute) is None
        ):
            return True

    return False


# ---------------------------
#   _check_entity_exists
# ---------------------------
async def _check_entity_exists(hass, platform, obj, uid) -> None:  # pragma: no cover
    """Add obj to HA if it is not yet registered or has been removed."""
    entity_registry = er.async_get(hass)
    if uid:
        unique_id = f"{obj._inst.lower()}-{obj.entity_description.key}-{slugify(str(obj._data[obj.entity_description.data_reference]).lower())}"
    else:
        unique_id = f"{obj._inst.lower()}-{obj.entity_description.key}"

    entity_id = entity_registry.async_get_entity_id(platform.domain, DOMAIN, unique_id)
    entity = entity_registry.async_get(entity_id)
    if entity is None or (
        (entity_id not in platform.entities) and (entity.disabled is False)
    ):
        _LOGGER.debug("Add entity %s", entity_id)
        await platform.async_add_entities([obj])


# ---------------------------
#   _run_entity_setup_loop
# ---------------------------
async def _run_entity_setup_loop(  # pragma: no cover
    hass, platform, config_entry, dispatcher, descriptions, coordinator
) -> None:
    """Iterate entity descriptions and add any missing entities to HA."""
    for entity_description in descriptions:
        data = coordinator.data[entity_description.data_path]
        if not entity_description.data_reference:
            if data.get(entity_description.data_attribute) is None:
                continue
            obj = dispatcher[entity_description.func](coordinator, entity_description)
            await _check_entity_exists(hass, platform, obj, None)
        else:
            for uid in data:
                if _skip_sensor(config_entry, entity_description, data, uid):
                    continue
                obj = dispatcher[entity_description.func](
                    coordinator, entity_description, uid
                )
                await _check_entity_exists(hass, platform, obj, uid)


# ---------------------------
#   async_add_entities
# ---------------------------
async def async_add_entities(  # pragma: no cover
    hass: HomeAssistant, config_entry: ConfigEntry, dispatcher: dict[str, Callable]
):
    """Add entities."""
    platform = ep.async_get_current_platform()
    services = platform.platform.SENSOR_SERVICES
    descriptions = platform.platform.SENSOR_TYPES

    for service in services:
        platform.async_register_entity_service(service[0], service[1], service[2])

    @callback
    async def async_update_controller(coordinator):
        """Update the values of the controller."""
        await _run_entity_setup_loop(
            hass, platform, config_entry, dispatcher, descriptions, coordinator
        )

    await async_update_controller(
        hass.data[DOMAIN][config_entry.entry_id].data_coordinator
    )

    unsub = async_dispatcher_connect(hass, "update_sensors", async_update_controller)
    config_entry.async_on_unload(unsub)


_MikrotikCoordinatorT = TypeVar(
    "_MikrotikCoordinatorT",
    bound=MikrotikCoordinator | MikrotikTrackerCoordinator,
)


# ---------------------------
#   MikrotikEntity
# ---------------------------
class MikrotikEntity(CoordinatorEntity[_MikrotikCoordinatorT], Entity):
    """Define entity"""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MikrotikCoordinator,
        entity_description,
        uid: str | None = None,
    ):
        """Initialize entity"""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._inst = coordinator.config_entry.data[CONF_NAME]
        self._config_entry = self.coordinator.config_entry
        self._attr_extra_state_attributes = {ATTR_ATTRIBUTION: ATTRIBUTION}
        self._uid = uid
        self._data = coordinator.data[self.entity_description.data_path]
        if self._uid:
            self._data = coordinator.data[self.entity_description.data_path][self._uid]

        self._attr_name = self.custom_name

    @callback
    def _handle_coordinator_update(self) -> None:
        self._data = self.coordinator.data[self.entity_description.data_path]
        if self._uid:
            self._data = self.coordinator.data[self.entity_description.data_path][
                self._uid
            ]
        super()._handle_coordinator_update()

    @property
    def custom_name(self) -> str:
        """Return the name for this entity"""
        if not self._uid:
            if self.entity_description.data_name_comment and self._data.get("comment"):
                return f"{self._data['comment']}"

            return f"{self.entity_description.name}"

        if self.entity_description.data_name_comment and self._data.get("comment"):
            return f"{self._data['comment']}"

        if self.entity_description.name:
            if (
                self._data[self.entity_description.data_reference]
                == self._data[self.entity_description.data_name]
            ):
                return f"{self.entity_description.name}"

            return f"{self._data[self.entity_description.data_name]} {self.entity_description.name}"

        return f"{self._data[self.entity_description.data_name]}"

    @property
    def unique_id(self) -> str:
        """Return a unique id for this entity"""
        if self._uid:
            return f"{self._inst.lower()}-{self.entity_description.key}-{slugify(str(self._data[self.entity_description.data_reference]).lower())}"
        else:
            return f"{self._inst.lower()}-{self.entity_description.key}"

    # @property
    # def available(self) -> bool:
    #     """Return if controller is available"""
    #     return self.coordinator.connected()

    @property
    def device_info(self) -> DeviceInfo:
        """Return a description for device registry."""
        dev_connection = DOMAIN
        dev_connection_value = self.entity_description.data_reference
        dev_group = self.entity_description.ha_group
        if self.entity_description.ha_group == "System":
            dev_group = self.coordinator.data["resource"]["board-name"]
            dev_connection_value = self.coordinator.data["routerboard"]["serial-number"]

        if self.entity_description.ha_group.startswith("data__"):
            dev_group = self.entity_description.ha_group[6:]
            if dev_group in self._data:
                dev_group = self._data[dev_group]
                dev_connection_value = dev_group

        if self.entity_description.ha_connection:
            dev_connection = self.entity_description.ha_connection

        if self.entity_description.ha_connection_value:
            dev_connection_value = self.entity_description.ha_connection_value
            if dev_connection_value.startswith("data__"):
                dev_connection_value = dev_connection_value[6:]
                dev_connection_value = self._data.get(
                    dev_connection_value, dev_connection_value
                )

        if self.entity_description.ha_group == "System":
            return DeviceInfo(
                connections={(dev_connection, f"{dev_connection_value}")},
                identifiers={(dev_connection, f"{dev_connection_value}")},
                name=f"{self._inst} {dev_group}",
                model=f"{self.coordinator.data['resource']['board-name']}",
                manufacturer=f"{self.coordinator.data['resource']['platform']}",
                sw_version=f"{self.coordinator.data['resource']['version']}",
                configuration_url=f"http://{self.coordinator.config_entry.data[CONF_HOST]}",
            )
        elif "mac-address" in self.entity_description.data_reference:
            dev_group = self._data[self.entity_description.data_name]
            dev_manufacturer = ""
            if dev_connection_value in self.coordinator.data["host"]:
                dev_group = self.coordinator.data["host"][dev_connection_value][
                    "host-name"
                ]
                dev_manufacturer = self.coordinator.data["host"][dev_connection_value][
                    "manufacturer"
                ]

            return DeviceInfo(
                connections={(dev_connection, f"{dev_connection_value}")},
                name=f"{dev_group}",
                manufacturer=f"{dev_manufacturer}",
                via_device=(
                    DOMAIN,
                    f"{self.coordinator.data['routerboard']['serial-number']}",
                ),
            )
        else:
            return DeviceInfo(
                connections={(dev_connection, f"{dev_connection_value}")},
                name=f"{self._inst} {dev_group}",
                model=f"{self.coordinator.data['resource']['board-name']}",
                manufacturer=f"{self.coordinator.data['resource']['platform']}",
                via_device=(
                    DOMAIN,
                    f"{self.coordinator.data['routerboard']['serial-number']}",
                ),
            )

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return the state attributes."""
        attributes = super().extra_state_attributes
        _copy_attrs(
            attributes, self._data, self.entity_description.data_attributes_list
        )
        return attributes

    async def start(self):  # pragma: no cover
        """Dummy run function"""
        raise NotImplementedError()

    async def stop(self):  # pragma: no cover
        """Dummy stop function"""
        raise NotImplementedError()

    async def restart(self):  # pragma: no cover
        """Dummy restart function"""
        raise NotImplementedError()

    async def reload(self):  # pragma: no cover
        """Dummy reload function"""
        raise NotImplementedError()
