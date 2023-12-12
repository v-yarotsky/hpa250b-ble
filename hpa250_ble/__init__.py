import asyncio
import time
import binascii
import platform
import sys
import struct
import logging

from bleak import BleakClient
from bleak.uuids import normalize_uuid_16, uuid16_dict, uuidstr_to_str

from .reconcile import reconcile
from .state import State
from .command import Command
from .enums import Preset, Backlight, VOCLight

logging.basicConfig(level=logging.INFO)

uuid16_lookup = {v: normalize_uuid_16(k) for k, v in uuid16_dict.items()}

SYSTEM_ID_UUID = uuid16_lookup["System ID"]
MODEL_NBR_UUID = uuid16_lookup["Model Number String"]
DEVICE_NAME_UUID = uuid16_lookup["Device Name"]
MANUFACTURER_NAME_UUID = uuid16_lookup["Manufacturer Name String"]
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

        # byte 1
        IS_OFF = 0
        IS_ON = 1 << 0
        IS_VOC_SET = 1 << 1
        IS_POLLEN_SET = 1 << 2
        IS_GERM = 1 << 3
        IS_GENERAL = 1 << 4
        IS_ALLERGEN = 1 << 5
        IS_TURBO = 1 << 6

        # byte 2
        BACKLIGHT_FULL = 0
        BACKLIGHT_DIM = 1
        BACKLIGHT_OFF = 2

        VOC_LIGHT_GREEN = 0
        VOC_LIGHT_AMBER = 1
        VOC_LIGHT_RED = 2

        def on_notify(ch, dt):
            logging.info(f"got characteristic: {ch}, data: {binascii.hexlify(dt)}")
            speed, lights, timer = struct.unpack("xBBxB14x", dt)
            logging.info(f"Off: {bool(speed & IS_OFF)}")
            logging.info(f"On: {bool(speed & IS_ON)}")
            logging.info(f"VOC: {bool(speed & IS_VOC_SET)}")
            logging.info(f"Pollen: {bool(speed & IS_POLLEN_SET)}")
            logging.info(f"Germ: {bool(speed & IS_GERM)}")
            logging.info(f"General: {bool(speed & IS_GENERAL)}")
            logging.info(f"Allergen: {bool(speed & IS_ALLERGEN)}")
            logging.info(f"Turbo: {bool(speed & IS_TURBO)}")

            voc_light = lights >> 2  # first 6 bits
            backlight = lights & 0b11  # last 2 bits
            logging.info(f"Light byte: {format(lights, 'b').rjust(8, '0')}")
            logging.info(f"VOC green: {voc_light == VOC_LIGHT_GREEN}")
            logging.info(f"VOC amber: {voc_light == VOC_LIGHT_AMBER}")
            logging.info(f"VOC red: {voc_light == VOC_LIGHT_RED}")
            logging.info(f"Backlight full: {backlight == BACKLIGHT_FULL}")
            logging.info(f"Backlight dim: {backlight == BACKLIGHT_DIM}")
            logging.info(f"Backlight off: {backlight == BACKLIGHT_OFF}")

            logging.info(f"Timer: {timer}")

        await client.start_notify(normalize_uuid_16(0xFFE4), callback=on_notify)

        async def send_command(cmd: bytes):
            logging.info(f"Sending command {binascii.hexlify(cmd)}")
            await client.write_gatt_char(
                normalize_uuid_16(0xFFE9),
                cmd,
                response=True,
            )
            time.sleep(2)

        # byte 1
        PREAMBLE = 0b10100101

        # byte 2
        TOGGLE_POWER = 1 << 0
        SPEED_GERM = 1 << 1
        SPEED_GENERAL = 1 << 2
        SPEED_ALLERGEN = 1 << 3
        SPEED_TURBO = 1 << 4
        SPEED_VOC = 1 << 5

        # byte 3
        TIMER_UP = 1 << 0
        TIMER_DOWN = 1 << 1
        LIGHT_CYCLE = 1 << 2
        TOGGLE_POLLEN = 1 << 3

        await send_command(
            struct.pack(
                "3B17x",
                PREAMBLE,
                SPEED_GERM,
                0,
            )
        )


# Command
# Command size is 40 bytes
# Can be OR-ed
#
#                  SP
# Toggle         a501000000000000000000000000000000000000  00000001
# Germ           a502000000000000000000000000000000000000  00000010
# General        a504000000000000000000000000000000000000  00000100
# Allergy        a508000000000000000000000000000000000000  00001000
# Toggle Turbo   a510000000000000000000000000000000000000  00010000
# Toggle VOC     a520000000000000000000000000000000000000  00100000

# Timer up       a500010000000000000000000000000000000000  00000001
# Timer down     a500020000000000000000000000000000000000  00000010
# Light cycle    a500040000000000000000000000000000000000  00000100
# Toggle Pollen  a500080000000000000000000000000000000000  00001000

# State
# State size is  38 bytes
#
#                  SPLT  TM
# state off:     a5000000001800000000000000000000000000
# state germ:    a5090000001800000000000000000000000000
# state generic: a5110000001800000000000000000000000000
# state allergy  a5210000001800000000000000000000000000
# turbo on       a5410000001800000000000000000000000000
# auto on:       a5030400001800000000000000000000000000
# alrgy auto on: a5070400001800000000000000000000000000
# lights ful:    a5210400001800000000000000000000000000 - allergy
# lights dim:    a5210500001800000000000000000000000000 - allergy
# lights off:    a5210600001800000000000000000000000000 - allergy
# allergy on:    a5050400001800000000000000000000000000
# timer 01h:     a5070000011800000000000000000000000000
# timer 02h:     a5070000021800000000000000000000000000
# timer 03h:     a5070000031800000000000000000000000000
# timer 04h:     a5070000041800000000000000000000000000
# timer 05h:     a5070000051800000000000000000000000000
# timer 06h:     a5070000061800000000000000000000000000
# timer 07h:     a5070000071800000000000000000000000000
# timer 08h:     a5070000081800000000000000000000000000
# timer 09h:     a5070000091800000000000000000000000000
# timer 10h:     a50700000a1800000000000000000000000000
# timer 11h:     a50700000b1800000000000000000000000000
# timer 12h:     a50700000c1800000000000000000000000000
# timer 13h:     a50700000d1800000000000000000000000000
# timer 14h:     a50700000e1800000000000000000000000000
# timer 15h:     a50700000f1800000000000000000000000000
# timer 16h:     a5070000101800000000000000000000000000
# timer 17h:     a5070000111800000000000000000000000000
# timer 18h:     a5070000121800000000000000000000000000

#                a5030500051800000000000000000000000000 - dim, auto, general
#                a5030100051800000000000000000000000000 - dim, auto, germ

# bit order: <preamble> 0 <turbo set> <allergy set> <generic set> <germ set> <pollen set> <auto set> <power set> <6-bit auto speed spec> <2 bit light spec> <pad byte> <1 byte timer spec>

# Speeds:
# - 00 - off                                 00000000
# - 09 - germ                                00001001
# - 11 - generic                             00010001
# - 21 - allergy                             00100001
# - 41 - turbo                               01000001
# - 03 - voc sensor                          00000011
# - 05 - pollen auto-set                     00000101
# - 07 - voc sensor with pollen auto-set     00000111

# Light:
# - 00 - auto speed germ, light full         00000000
# - 01 - auto speed germ, light dim          00000001
# - 02 - auto speed germ, light full         00000010
# - 03 - auto speed general, light full      00000100
# - 04 - auto speed general, light dim       00000101
# - 05 - auto speed general, light off       00000110
# - 06 - auto speed alelrgen, light full     00001000
# - 07 - auto speed alelrgen, light dim      00001001
# - 08 - auto speed alelrgen, light off      00001010

# Timer:
# - 00 - 0h
# - ..
# - 12 - 18h


def mac_addr_str_to_bytes(mac_addr_str: str) -> bytes:
    """Converts MAC address string like 00:10:20:30:40:50 to bytes"""
    return struct.pack("6B", *[int(b, 16) for b in mac_addr_str.split(":")])


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
