import pytest
import binascii
from bleak.backends.device import BLEDevice
from typing import Awaitable, Callable
from hpa250b_ble.command import Command
from hpa250b_ble.const import SYSTEM_ID_UUID, COMMAND_UUID, STATE_UUID
from hpa250b_ble.enums import Preset, Backlight
from hpa250b_ble.exc import BTClientDisconnectedError
from hpa250b_ble.hpa250b import BTClient, HPA250B, Delegate
from hpa250b_ble.state import State


class FakeBTClient(BTClient):
    def __init__(self, initial_state=State.empty()):
        self._is_connected = False
        self.notify_callback: Callable[[bytes], Awaitable[None]] | None = None
        self.next_notification: bytes | None = None
        self.commands: list[bytes] = []
        self.initial_state = initial_state

    @property
    def address(self) -> str:
        return "00:01:02:03:04:05"

    @property
    def name(self) -> str:
        return "mydevice"

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
            await self.notify_callback(self.next_notification)

    async def start_notify(
        self, uuid: str, callback: Callable[[bytes], Awaitable[None]]
    ):
        if uuid != STATE_UUID:
            raise ValueError(f"unexpected characteristic watch: {uuid}")

        self.notify_callback = callback

    def setup_notification(self, data: bytes):
        self.next_notification = data


class FakeDelegate(Delegate):
    def __init__(self, client: FakeBTClient | None):
        self.client = client

    async def make_bt_client(self, *_) -> BTClient | None:
        return self.client

    async def handle_update(self, *_):
        pass


class TestHPA250B:
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
        c = FakeBTClient(initial_state)
        d = HPA250B(FakeDelegate(c))

        await d.connect()

        assert c.commands == [b"MAC+" + binascii.unhexlify("0035FF091AC0")]
        assert d.is_connected
        assert d.current_state == initial_state

    @pytest.mark.asyncio
    async def test_send_command(self):
        c = FakeBTClient()
        d = HPA250B(FakeDelegate(c))

        await d.connect()

        cmd = Command().toggle_power()
        c.setup_notification(
            State(True, Preset.GENERAL, Backlight.ON, None, None).bytes
        )
        await d.apply_command(cmd)

        assert cmd.bytes in c.commands

    @pytest.mark.asyncio
    async def test_raises_when_sending_on_disconnected_client(self):
        c = FakeBTClient()
        d = HPA250B(FakeDelegate(c))

        with pytest.raises(BTClientDisconnectedError):
            await d.apply_command(Command().toggle_power())

        await d.connect()
        await d.disconnect()

        with pytest.raises(BTClientDisconnectedError):
            await d.apply_command(Command().toggle_power())
