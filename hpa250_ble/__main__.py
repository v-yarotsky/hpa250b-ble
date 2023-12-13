import asyncio
import platform
import logging

from bleak import BleakScanner
from hpa250_ble import State, BleakHPA250B, reconcile, Preset, Backlight

logging.basicConfig(level=logging.INFO)

ADDRESS = (
    "00:35:FF:09:1A:C0"
    if platform.system() != "Darwin"
    else "890A004D-331D-7C0D-B085-253BB7FBCB5B"
)


async def main(address: str):
    ble_device = await BleakScanner.find_device_by_address(address)

    logging.info(f"Found device: {ble_device}")
    d = BleakHPA250B(ble_device)

    logging.info(f"Connecting to {ble_device.name}")
    await d.connect()
    logging.info(f"Connected: {d.current_state}")

    desired = State(
        is_on=True,
        preset=Preset.AUTO_VOC_POLLEN,
        backlight=Backlight.DIM,
        voc_light=None,
        timer=None,
    )
    await reconcile(d, desired)

    logging.info(f"State after reconciliation: {d.current_state}")


if __name__ == "__main__":
    asyncio.run(main(ADDRESS))
