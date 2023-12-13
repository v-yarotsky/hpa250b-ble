import pytest
import binascii
from bleak.backends.device import BLEDevice
from typing import Callable
from hpa250_ble.hpa250b import BTClient, BleakHPA250B
from hpa250_ble.const import SYSTEM_ID_UUID, COMMAND_UUID, STATE_UUID
from hpa250_ble.state import State
from hpa250_ble.enums import Preset, Backlight


class FakeBTClient(BTClient):
    def __init__(self):
        self._is_connected = True
        self.notify_callbacks: dict[str, Callable[[bytes], None]] = {}
        self.commands: list[bytes] = []

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    async def disconnect(self):
        self._is_connected = False

    async def read_gatt_char(self, uuid: str) -> bytes:
        if uuid == SYSTEM_ID_UUID:
            return binascii.unhexlify("C01A090000FF3500")
        raise ValueError(f"unexpected characteristic read: {uuid}")

    async def write_gatt_char(self, uuid: str, data: bytes):
        if uuid == COMMAND_UUID:
            self.commands.append(data)
            return
        raise ValueError(f"unexpected characteristic write: {uuid}")

    async def start_notify(self, uuid: str, callback: Callable[[bytes], None]):
        self.notify_callbacks[uuid] = callback

    def notify(self, uuid: str, data: bytes):
        self.notify_callbacks[uuid](data)


class TestBleakHPA250B:
    @pytest.mark.asyncio
    async def test_handshake(self):
        d = BleakHPA250B(
            BLEDevice(
                address="00:01:02:03:04:05", name="myhpa250b", details=None, rssi=90
            )
        )
        c = FakeBTClient()

        await d.connect(lambda *_: c)

        assert c.commands == [b"MAC+" + binascii.unhexlify("0035FF091AC0")]
        assert d.is_connected

        c.notify(
            STATE_UUID,
            State(
                is_on=True,
                preset=Preset.GENERAL,
                backlight=Backlight.ON,
                voc_light=None,
                timer=None,
            ).bytes,
        )
