import argparse
import asyncio
import logging
from hpa250b_ble import State, HPA250B, BleakDelegate, reconcile, Preset, Backlight

logging.basicConfig(level=logging.INFO)


async def main():
    parser = argparse.ArgumentParser(
        description="Example program to test HPA250B control"
    )

    parser.add_argument(
        "--address", type=str, help="Bluetooth device address (UUID on macOS)"
    )

    args = parser.parse_args()

    d = HPA250B(BleakDelegate(args.address))

    logging.info(f"Connecting")
    await d.connect()
    logging.info(f"Connected to {d.name}: {d.current_state}")

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
