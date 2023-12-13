import asyncio
import time
import binascii
import platform
import struct
import logging

from bleak import BleakClient
from bleak.uuids import normalize_uuid_16, uuid16_dict

from hpa250_ble import Command, State

logging.basicConfig(level=logging.INFO)

uuid16_lookup = {v: normalize_uuid_16(k) for k, v in uuid16_dict.items()}

SYSTEM_ID_UUID = uuid16_lookup["System ID"]
PNP_ID_UUID = uuid16_lookup["PnP ID"]

ADDRESS = (
    "00:35:FF:09:1A:C0"
    if platform.system() != "Darwin"
    else "890A004D-331D-7C0D-B085-253BB7FBCB5B"
)


async def main(address: str):
    async with BleakClient(address) as client:
        logging.info(f"Connected: {client.is_connected}")
        logging.info(f"Address: {client.address}")

        system_id = await client.read_gatt_char(SYSTEM_ID_UUID)
        logging.info(f"Raw system id: {system_id}")
        logging.info(f"Manufacturer ID: {extract_manufacturer_id(system_id)}")
        logging.info(f"System ID: {format_system_id_as_mac(system_id)}")

        mac_bytes = bytearray(
            reversed(struct.unpack("BBBxxBBB", system_id))
        )  # System ID "C01A090000FF3500" encodes MAC 00:35:FF:09:1A:C0
        logging.info(f"MAC: {binascii.hexlify(mac_bytes)}")

        pnp_id = await client.read_gatt_char(PNP_ID_UUID)
        logging.info(f"Raw PnP ID: {pnp_id} (size: {len(pnp_id)})")
        logging.info(f"Parsed PnP ID: {extract_pnp_id_fields(pnp_id)}")

        for s in client.services:
            logging.info(f"Service: {s}")
            for c in s.characteristics:
                logging.info(f"\t{c}")

        # This is some sort of auth handshake
        logging.info("Sending handshake")
        await client.write_gatt_char(
            normalize_uuid_16(0xFFE9),
            b"MAC+" + mac_bytes,
            response=True,
        )

        def on_notify(ch, dt):
            logging.info(f"got characteristic: {ch}, data: {binascii.hexlify(dt)}")
            state = State.from_bytes(dt)
            logging.info(f"State: {state}")

        await client.start_notify(normalize_uuid_16(0xFFE4), callback=on_notify)

        async def send_command(cmd: bytes):
            logging.info(f"Sending command {binascii.hexlify(cmd)}")
            await client.write_gatt_char(
                normalize_uuid_16(0xFFE9),
                cmd,
                response=True,
            )
            time.sleep(2)

        await send_command(Command().bytes)


def extract_pnp_id_fields(pnp_id_bytes):
    # Assuming little-endian byte order
    vendor_id_source, _, vendor_id, product_id, product_version = struct.unpack(
        "<BBHHH", pnp_id_bytes.rjust(8, b"\x00")
    )

    return {
        "Vendor ID Source": vendor_id_source,
        "Vendor ID": vendor_id,
        "Product ID": product_id,
        "Product Version": product_version,
    }


def extract_manufacturer_id(system_id_bytes: bytes):
    # Assuming little-endian byte order (you may need to adjust based on the device specification)
    manufacturer_id = struct.unpack("<H", system_id_bytes[:2])[0]
    return manufacturer_id


def format_system_id_as_mac(system_id_bytes: bytes):
    # Convert each byte to a two-digit hexadecimal representation
    hex_values = [format(byte, "02X") for byte in system_id_bytes]

    # Join the hex values with colons to form the MAC address format
    mac_address = ":".join(hex_values)

    return mac_address


if __name__ == "__main__":
    asyncio.run(main(ADDRESS))
