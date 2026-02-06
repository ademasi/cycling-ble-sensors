"""Sensor platform for Cycling BLE Sensors."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CyclingBLEConfigEntry, CyclingBLECoordinator
from .const import DOMAIN


async def async_setup_entry(
    hass, entry: CyclingBLEConfigEntry, async_add_entities
) -> None:
    """Set up Cycling BLE Sensor entities."""
    coordinator = entry.runtime_data
    async_add_entities([CyclingBLEBatterySensor(coordinator, entry)])


class CyclingBLEBatterySensor(
    CoordinatorEntity[CyclingBLECoordinator], SensorEntity
):
    """Battery level sensor for a cycling BLE device."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_name = "Battery"

    def __init__(
        self,
        coordinator: CyclingBLECoordinator,
        entry: CyclingBLEConfigEntry,
    ) -> None:
        """Initialize the battery sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.unique_id}_battery"
        manufacturer = None
        if coordinator.device_config:
            manufacturer = coordinator.device_config.get("manufacturer")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
            name=coordinator.device_name,
            manufacturer=manufacturer,
        )

    @property
    def native_value(self) -> int | None:
        """Return the battery level."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("battery")
