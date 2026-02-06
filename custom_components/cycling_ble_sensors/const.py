"""Constants for the Cycling BLE Sensors integration."""

DOMAIN = "cycling_ble_sensors"

BATTERY_LEVEL_UUID = "00002a19-0000-1000-8000-00805f9b34fb"

# Registry of supported devices keyed by local_name prefix.
# Adding future cycling devices means adding entries here.
SUPPORTED_DEVICES = {
    "Ion": {  # Matches "Ion 200 RT", "Ion Pro RT", etc.
        "manufacturer": "Trek Bicycle",
        "battery_uuid": BATTERY_LEVEL_UUID,
    },
}
