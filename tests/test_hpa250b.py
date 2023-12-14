from hpa250b_ble.command import Command
from hpa250b_ble.exc import BTClientDisconnectedError
import pytest
import binascii
from bleak.backends.device import BLEDevice
from typing import Callable, Optional
from hpa250b_ble.hpa250b import BTClient, BleakHPA250B
from hpa250b_ble.const import SYSTEM_ID_UUID, COMMAND_UUID, STATE_UUID
from hpa250b_ble.state import State
from hpa250b_ble.enums import Preset, Backlight


class FakeBTClient(BTClient):
    def __init__(self, initial_state=State.empty()):
        self._is_connected = False
        self.notify_callback: Optional[Callable[[bytes], None]] = None
        self.next_notification: Optional[bytes] = None
        self.commands: list[bytes] = []
        self.initial_state = initial_state

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    async def connect(self):
        self.setup_notification(self.initial_state.bytes)
        self._is_connected = True

    async def disconnect(self):
        self._is_connected = False

    async def read_gatt_char(self, uuid: str) -> bytes:
        if uuid != SYSTEM_ID_UUID:
            raise ValueError(f"unexpected characteristic read: {uuid}")

        return binascii.unhexlify("C01A090000FF3500")

    async def write_gatt_char(self, uuid: str, data: bytes):
        if uuid != COMMAND_UUID:
            raise ValueError(f"unexpected characteristic write: {uuid}")

        self.commands.append(data)
        if self.notify_callback is not None and self.next_notification is not None:
            self.notify_callback(self.next_notification)

    async def start_notify(self, uuid: str, callback: Callable[[bytes], None]):
        if uuid != STATE_UUID:
            raise ValueError(f"unexpected characteristic watch: {uuid}")

        self.notify_callback = callback

    def setup_notification(self, data: bytes):
        self.next_notification = data


class TestBleakHPA250B:
    def setup_method(self):
        self.ble_device = BLEDevice(
            address="00:01:02:03:04:05", name="myhpa250b", details=None, rssi=90
        )

    @pytest.mark.asyncio
    async def test_handshake(self):
        initial_state = State(
            is_on=True,
            preset=Preset.GENERAL,
            backlight=Backlight.ON,
            voc_light=None,
            timer=None,
        )
        d = BleakHPA250B(self.ble_device)
        c = FakeBTClient(initial_state)

        await d.connect(lambda *_: c)

        assert c.commands == [b"MAC+" + binascii.unhexlify("0035FF091AC0")]
        assert d.is_connected
        assert d.current_state == initial_state

    @pytest.mark.asyncio
    async def test_send_command(self):
        d = BleakHPA250B(self.ble_device)
        c = FakeBTClient()

        await d.connect(lambda *_: c)

        cmd = Command().toggle_power()
        c.setup_notification(
            State(True, Preset.GENERAL, Backlight.ON, None, None).bytes
        )
        await d.apply_command(cmd)

        assert cmd.bytes in c.commands

    @pytest.mark.asyncio
    async def test_raises_when_sending_on_disconnected_client(self):
        d = BleakHPA250B(self.ble_device)

        with pytest.raises(BTClientDisconnectedError):
            await d.apply_command(Command().toggle_power())

        c = FakeBTClient()
        await d.connect(lambda *_: c)
        await d.disconnect()

        with pytest.raises(BTClientDisconnectedError):
            await d.apply_command(Command().toggle_power())
