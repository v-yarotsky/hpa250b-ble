# Honeywell HPA250B BLE library

Controls Honeywell HPA250B device over BLE using the [Bleak](https://github.com/hbldh/bleak) library.

## Example

```python
import asyncio

from bleak import BleakScanner
from hpa250b_ble import BleakHPA250B, reconcile, State, Preset, Backlight


ADDRESS = "00:00:00:00:00:00"  # your device MAC address (UUID on macOS)
ble_device = await BleakScanner.find_device_by_address(ADDRESS)

d = BleakHPA250B(ble_device)
await d.connect()

desired = State(
    is_on=True,
    preset=Preset.AUTO_VOC_POLLEN,
    backlight=Backlight.DIM,
    voc_light=None,
    timer=12,
)
await reconcile(d, desired)
```
