# Cycling BLE Sensors

Home Assistant custom integration for cycling BLE devices that require active GATT connections (not passive advertisement parsing).

## Supported Devices

| Device | Manufacturer | Sensors |
|--------|-------------|---------|
| Bontrager Ion 200 RT | Trek Bicycle | Battery |
| Bontrager Ion Pro RT | Trek Bicycle | Battery |

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu → **Custom repositories**
3. Add `https://github.com/ademasi/cycling-ble-sensors` as an **Integration**
4. Search for "Cycling BLE Sensors" and install
5. Restart Home Assistant

### Manual

Copy `custom_components/cycling_ble_sensors/` to your Home Assistant `custom_components/` directory and restart.

## Setup

The integration uses Bluetooth discovery. When your device is in range:

1. Home Assistant will show a notification: "Cycling BLE Sensors discovered [device name]"
2. Click **Configure** and confirm
3. A battery sensor will appear (e.g., `sensor.ion_200_rt_battery`)

The battery level is polled every 10 minutes via an active BLE connection.

## Adding Device Support

To add a new cycling BLE device, add an entry to `SUPPORTED_DEVICES` in `const.py`:

```python
SUPPORTED_DEVICES = {
    "Ion": {  # existing
        "manufacturer": "Trek Bicycle",
        "battery_uuid": BATTERY_LEVEL_UUID,
    },
    "Varia": {  # new device
        "manufacturer": "Garmin",
        "battery_uuid": BATTERY_LEVEL_UUID,
    },
}
```

Then add a matching BLE matcher in `manifest.json`:

```json
"bluetooth": [
    {"local_name": "Ion*", "connectable": true},
    {"local_name": "Varia*", "connectable": true}
]
```
