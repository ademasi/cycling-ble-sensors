"""Cycling BLE Sensors integration for Home Assistant."""

from __future__ import annotations

import logging
from datetime import timedelta

from bleak import BleakClient
from bleak.exc import BleakError

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import BATTERY_LEVEL_UUID, DOMAIN, SUPPORTED_DEVICES

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]
POLL_INTERVAL = timedelta(minutes=10)


type CyclingBLEConfigEntry = ConfigEntry[CyclingBLECoordinator]


class CyclingBLECoordinator(DataUpdateCoordinator[dict[str, int]]):
    """Coordinator that polls battery level over an active BLE connection."""

    def __init__(self, hass: HomeAssistant, entry: CyclingBLEConfigEntry) -> None:
        """Initialize the coordinator."""
        self.address: str = entry.data[CONF_ADDRESS]
        self.device_name: str = entry.data["name"]

        # Look up device config from prefix match
        self.device_config: dict | None = None
        for prefix, config in SUPPORTED_DEVICES.items():
            if self.device_name.startswith(prefix):
                self.device_config = config
                break

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.address}",
            update_interval=POLL_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, int]:
        """Connect to the device and read battery level."""
        device = bluetooth.async_ble_device_from_address(self.hass, self.address)
        if device is None:
            raise UpdateFailed(f"Device {self.address} not available")

        try:
            async with BleakClient(device) as client:
                raw = await client.read_gatt_char(BATTERY_LEVEL_UUID)
                battery = raw[0]
                _LOGGER.debug(
                    "Read battery=%d%% from %s (%s)",
                    battery,
                    self.device_name,
                    self.address,
                )
                return {"battery": battery}
        except BleakError as err:
            raise UpdateFailed(f"BLE communication error: {err}") from err


async def async_setup_entry(hass: HomeAssistant, entry: CyclingBLEConfigEntry) -> bool:
    """Set up Cycling BLE Sensors from a config entry."""
    coordinator = CyclingBLECoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: CyclingBLEConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
