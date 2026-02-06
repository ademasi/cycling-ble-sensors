"""Config flow for Cycling BLE Sensors."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS

from .const import DOMAIN, SUPPORTED_DEVICES

_LOGGER = logging.getLogger(__name__)


def _device_matches(name: str) -> bool:
    """Check if a device name matches any supported prefix."""
    return any(name.startswith(prefix) for prefix in SUPPORTED_DEVICES)


class CyclingBLESensorsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cycling BLE Sensors."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle Bluetooth discovery."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        name = discovery_info.name
        if _device_matches(name):
            self._discovery_info = discovery_info
            self.context["title_placeholders"] = {"name": name}
            return await self.async_step_bluetooth_confirm()

        return self.async_abort(reason="not_supported")

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm Bluetooth discovery."""
        assert self._discovery_info is not None

        if user_input is not None:
            return self.async_create_entry(
                title=self._discovery_info.name,
                data={
                    CONF_ADDRESS: self._discovery_info.address,
                    "name": self._discovery_info.name,
                },
            )

        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={"name": self._discovery_info.name},
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle manual add — scan for matching BLE devices."""
        # Find matching devices from HA's Bluetooth scanner
        already_configured = self._async_current_ids()
        devices: dict[str, str] = {}
        for info in async_discovered_service_info(self.hass, connectable=True):
            if info.address in already_configured:
                continue
            if info.name and _device_matches(info.name):
                devices[info.address] = info.name

        if not devices:
            return self.async_abort(reason="no_devices_found")

        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            name = devices.get(address, address)
            await self.async_set_unique_id(address)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=name,
                data={CONF_ADDRESS: address, "name": name},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): vol.In(
                        {addr: f"{name} ({addr})" for addr, name in devices.items()}
                    ),
                }
            ),
        )
