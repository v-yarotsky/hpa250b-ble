import asyncio
import binascii
from bleak.backends.device import BLEDevice
from bleak import BleakClient
import struct
from typing import Callable, Protocol
from . import _LOGGER
from .command import Command
from .const import SYSTEM_ID_UUID, COMMAND_UUID, STATE_UUID
from .exc import BTClientDisconnectedError
from .models import HPA250B
from .state import State

UPDATE_TIMEOUT_SECONDS = 2


class BTClient(Protocol):
    @property
    def is_connected(self) -> bool:
        ...

    async def connect(self):
        ...

    async def disconnect(self):
        ...

    async def read_gatt_char(self, uuid: str) -> bytes:
        ...

    async def write_gatt_char(self, uuid: str, data: bytes):
        ...

    async def start_notify(self, uuid: str, callback: Callable[[bytes], None]):
        ...


class BleakBTClient(BTClient):
    def __init__(self, device: BLEDevice, disconnected_callback=Callable[[], None]):
        self._client = BleakClient(device, disconnected_callback=disconnected_callback)

    @property
    def is_connected(self) -> bool:
        return self._client.is_connected

    async def connect(self):
        await self._client.connect()

    async def disconnect(self):
        await self._client.disconnect()

    async def read_gatt_char(self, uuid: str) -> bytes:
        return await self._client.read_gatt_char(uuid)

    async def write_gatt_char(self, uuid: str, data: bytes):
        return await self._client.write_gatt_char(uuid, data, response=True)

    async def start_notify(self, uuid: str, callback: Callable[[bytes], None]):
        return await self._client.start_notify(uuid, lambda _, data: callback(data))


class DisconnectedBTClient(BTClient):
    def is_connected(self) -> bool:
        return False

    def connect(self):
        pass

    def disconnect(self):
        pass

    def read_gatt_char(self, *_) -> bytes:
        raise BTClientDisconnectedError("can't read GATT characteristic: not connected")

    def write_gatt_char(self, *_):
        raise BTClientDisconnectedError(
            "can't write GATT characteristic: not connected"
        )

    def start_notify(self, *_):
        raise BTClientDisconnectedError(
            "can't listen for GATT characteristic notifications: not connected"
        )


class BleakHPA250B(HPA250B):
    def __init__(self, ble_device: BLEDevice):
        self._device = ble_device
        self._state = State.empty()
        self._client: BTClient = DisconnectedBTClient()
        self._is_connected = False

        self.update_received = asyncio.Event()

    @property
    def is_connected(self):
        return self._is_connected

    @property
    def address(self):
        return self._device.address

    @property
    def name(self):
        return self._device.name or self._device.address

    async def connect(self, client_factory: Callable[..., BTClient] = BleakBTClient):
        if self.is_connected:
            _LOGGER.debug("connect: bluetooth client is already connected")
            return

        _LOGGER.debug("connecting")
        self._client = client_factory(self._device, self.disconnect)
        await self._client.connect()

        system_id = await self._client.read_gatt_char(SYSTEM_ID_UUID)
        _LOGGER.debug(f"system id: {binascii.hexlify(system_id)}")

        mac_bytes = bytearray(
            reversed(struct.unpack("BBBxxBBB", system_id))
        )  # System ID "C01A090000FF3500" encodes MAC 00:35:FF:09:1A:C0
        _LOGGER.debug(f"MAC: {binascii.hexlify(mac_bytes)}")
        _LOGGER.debug("sending handshake")

        self.update_received.clear()

        await self._client.start_notify(STATE_UUID, callback=self._handle_update)

        await self._client.write_gatt_char(
            COMMAND_UUID,
            b"MAC+" + mac_bytes,
        )
        await asyncio.wait_for(
            self.update_received.wait(), timeout=UPDATE_TIMEOUT_SECONDS
        )

        self._is_connected = True

    async def disconnect(self):
        if not self.is_connected:
            _LOGGER.debug("disconnect: bluetooth client is already disconnected")
            return
        _LOGGER.debug("disconnecting")
        await self._client.disconnect()
        self._client = DisconnectedBTClient()
        self._is_connected = False
        self._state = State.empty()

    @property
    def current_state(self) -> State:
        return self._state

    async def apply_command(self, cmd: Command):
        _LOGGER.debug(f"sending command {cmd}")
        self.update_received.clear()
        await self._client.write_gatt_char(COMMAND_UUID, cmd.bytes)
        await asyncio.wait_for(
            self.update_received.wait(), timeout=UPDATE_TIMEOUT_SECONDS
        )

    def _handle_update(self, data: bytes):
        old_state, self._state = self._state, State.from_bytes(data)
        _LOGGER.debug(f"updated state {old_state} -> {self._state}")
        self.update_received.set()