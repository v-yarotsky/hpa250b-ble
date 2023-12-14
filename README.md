# Honeywell HPA250B BLE library

Controls Honeywell HPA250B device over BLE using the [Bleak](https://github.com/hbldh/bleak) library.

## Example

```python
import asyncio

from hpa250b_ble import HPA250B, BleakDelegate, reconcile, State, Preset, Backlight


ADDRESS = "00:00:00:00:00:00"  # your device MAC address (UUID on macOS)

d = HPA250B(BleakDelegate(ADDRESS))
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
