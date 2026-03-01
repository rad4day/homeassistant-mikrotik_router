"""Tests for sensor type definitions.

These tests verify the fixes for:
- upstream #230: Temperature sensors should respect HA unit preference
- Redundant suggested_unit_of_measurement removal
"""

from homeassistant.const import (
    UnitOfTemperature,
    UnitOfElectricPotential,
    UnitOfElectricCurrent,
    UnitOfPower,
    UnitOfDataRate,
    UnitOfInformation,
)
from homeassistant.components.sensor import SensorDeviceClass

from custom_components.mikrotik_router.sensor_types import SENSOR_TYPES


def _get_sensor(key):
    """Get a sensor description by key."""
    for sensor in SENSOR_TYPES:
        if sensor.key == key:
            return sensor
    raise KeyError(f"Sensor {key!r} not found in SENSOR_TYPES")


# ---------------------------
#   Fix #230: Temperature unit conversion
# ---------------------------


TEMPERATURE_SENSOR_KEYS = [
    "system_temperature",
    "system_cpu-temperature",
    "system_switch-temperature",
    "system_board-temperature1",
    "system_phy-temperature",
]


class TestTemperatureSensorsUnitConversion:
    """Fix #230: Temperature sensors must not override HA's unit conversion.

    When suggested_unit_of_measurement equals native_unit_of_measurement,
    HA skips auto-conversion. Removing suggested_unit lets HA convert
    Celsius to Fahrenheit (or vice versa) based on user preference.
    """

    def test_temperature_sensors_have_no_suggested_unit(self):
        """No temperature sensor should set suggested_unit_of_measurement."""
        for key in TEMPERATURE_SENSOR_KEYS:
            sensor = _get_sensor(key)
            assert sensor.suggested_unit_of_measurement is None, (
                f"Sensor {key!r} has suggested_unit_of_measurement="
                f"{sensor.suggested_unit_of_measurement!r}. "
                f"This prevents HA from auto-converting to user's preferred unit."
            )

    def test_temperature_sensors_have_correct_native_unit(self):
        """All temperature sensors report in Celsius natively."""
        for key in TEMPERATURE_SENSOR_KEYS:
            sensor = _get_sensor(key)
            assert sensor.native_unit_of_measurement == UnitOfTemperature.CELSIUS

    def test_temperature_sensors_have_device_class(self):
        """All temperature sensors have the TEMPERATURE device class.

        This is what enables HA's automatic unit conversion.
        """
        for key in TEMPERATURE_SENSOR_KEYS:
            sensor = _get_sensor(key)
            assert sensor.device_class == SensorDeviceClass.TEMPERATURE

    def test_temperature_sensors_have_display_precision(self):
        """Temperature sensors should have display precision set."""
        for key in TEMPERATURE_SENSOR_KEYS:
            sensor = _get_sensor(key)
            assert sensor.suggested_display_precision is not None


# ---------------------------
#   Redundant suggested_unit removal (voltage/power)
# ---------------------------


VOLTAGE_SENSOR_KEYS = [
    "system_voltage",
    "system_psu1_voltage",
    "system_psu2_voltage",
]

POWER_SENSOR_KEYS = [
    "system_power-consumption",
    "system_poe_out_consumption",
]


class TestVoltageAndPowerSensorsNoRedundantUnit:
    """Voltage and power sensors should not set suggested_unit == native_unit.

    When they're the same unit, the attribute is a no-op and just adds
    clutter. Removing it keeps sensor definitions clean and consistent.
    """

    def test_voltage_sensors_no_redundant_suggested_unit(self):
        """Voltage sensors should not suggest the same unit as native."""
        for key in VOLTAGE_SENSOR_KEYS:
            sensor = _get_sensor(key)
            if sensor.suggested_unit_of_measurement is not None:
                assert (
                    sensor.suggested_unit_of_measurement
                    != sensor.native_unit_of_measurement
                ), (
                    f"Sensor {key!r} has redundant "
                    f"suggested_unit == native_unit == {sensor.native_unit_of_measurement!r}"
                )

    def test_power_sensors_no_redundant_suggested_unit(self):
        """Power sensors should not suggest the same unit as native."""
        for key in POWER_SENSOR_KEYS:
            sensor = _get_sensor(key)
            if sensor.suggested_unit_of_measurement is not None:
                assert (
                    sensor.suggested_unit_of_measurement
                    != sensor.native_unit_of_measurement
                ), (
                    f"Sensor {key!r} has redundant "
                    f"suggested_unit == native_unit == {sensor.native_unit_of_measurement!r}"
                )


# ---------------------------
#   Intentional unit conversions remain intact
# ---------------------------


class TestIntentionalUnitConversions:
    """Verify that intentional unit conversions (bytes->KB, A->mA) are kept."""

    def test_current_sensors_convert_ampere_to_milliampere(self):
        """PSU current sensors convert from A (native) to mA (suggested)."""
        for key in ["system_psu1_current", "system_psu2_current"]:
            sensor = _get_sensor(key)
            assert sensor.native_unit_of_measurement == UnitOfElectricCurrent.AMPERE
            assert (
                sensor.suggested_unit_of_measurement
                == UnitOfElectricCurrent.MILLIAMPERE
            )

    def test_traffic_sensors_convert_bytes_to_kilobytes(self):
        """Traffic rate sensors convert from B/s (native) to KB/s (suggested)."""
        sensor = _get_sensor("traffic_tx")
        assert sensor.native_unit_of_measurement == UnitOfDataRate.BYTES_PER_SECOND
        assert (
            sensor.suggested_unit_of_measurement == UnitOfDataRate.KILOBYTES_PER_SECOND
        )

    def test_data_sensors_convert_bytes_to_gigabytes(self):
        """Data volume sensors convert from B (native) to GB (suggested)."""
        sensor = _get_sensor("tx-total")
        assert sensor.native_unit_of_measurement == UnitOfInformation.BYTES
        assert sensor.suggested_unit_of_measurement == UnitOfInformation.GIGABYTES
