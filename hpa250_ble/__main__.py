import argparse
import asyncio
import logging
from bleak import BleakScanner
from hpa250_ble import State, BleakHPA250B, reconcile, Preset, Backlight

logging.basicConfig(level=logging.INFO)


async def main():
    parser = argparse.ArgumentParser(
        description="Example program to test HPA250B control"
    )

    parser.add_argument(
        "--address", type=str, help="Bluetooth device address (UUID on macOS)"
    )

    args = parser.parse_args()

    ble_device = await BleakScanner.find_device_by_address(args.address)

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
    asyncio.run(main())
