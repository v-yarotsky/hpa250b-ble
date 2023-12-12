import struct
from typing import cast
from . import const

# Command structure:
# byte 0: <preamble>
# byte 1: 0 0 <toggle voc set> <turbo set> <allergen set> <general set> <germ set> <toggle power set>
# byte 2: 0 0 0 0 <toggle pollen set> <cycle light set> <timer down set> <timer up set>
# rest:   pad with 0x00
_COMMAND_STRUCT_FORMAT = "3B17x"


class Command:
    _bytes: bytearray

    def __init__(self):
        self._bytes = bytearray([const.PREAMBLE, 0x00, 0x00])

    def toggle_power(self) -> "Command":
        self._bytes[1] |= const.COMMAND_TOGGLE_POWER
        return self

    @property
    def is_toggle_power(self) -> bool:
        return bool(self._bytes[1] & const.COMMAND_TOGGLE_POWER)

    def toggle_germ(self) -> "Command":
        self._bytes[1] |= const.COMMAND_TOGGLE_GERM
        return self

    @property
    def is_toggle_germ(self) -> bool:
        return bool(self._bytes[1] & const.COMMAND_TOGGLE_GERM)

    def toggle_general(self) -> "Command":
        self._bytes[1] |= const.COMMAND_TOGGLE_GENERAL
        return self

    @property
    def is_toggle_general(self) -> bool:
        return bool(self._bytes[1] & const.COMMAND_TOGGLE_GENERAL)

    def toggle_allergen(self) -> "Command":
        self._bytes[1] |= const.COMMAND_TOGGLE_ALLERGEN
        return self

    @property
    def is_toggle_allergen(self) -> bool:
        return bool(self._bytes[1] & const.COMMAND_TOGGLE_ALLERGEN)

    def toggle_turbo(self) -> "Command":
        self._bytes[1] |= const.COMMAND_TOGGLE_TURBO
        return self

    @property
    def is_toggle_turbo(self) -> bool:
        return bool(self._bytes[1] & const.COMMAND_TOGGLE_TURBO)

    def toggle_auto_voc(self) -> "Command":
        self._bytes[1] |= const.COMMAND_TOGGLE_VOC
        return self

    @property
    def is_toggle_auto_voc(self) -> bool:
        return bool(self._bytes[1] & const.COMMAND_TOGGLE_VOC)

    def toggle_auto_pollen(self) -> "Command":
        self._bytes[2] |= const.COMMAND_TOGGLE_POLLEN
        return self

    @property
    def is_toggle_auto_pollen(self) -> bool:
        return bool(self._bytes[2] & const.COMMAND_TOGGLE_POLLEN)

    def cycle_light(self) -> "Command":
        self._bytes[2] |= const.COMMAND_LIGHT_CYCLE
        return self

    @property
    def is_cycle_light(self) -> bool:
        return bool(self._bytes[2] & const.COMMAND_LIGHT_CYCLE)

    def timer_up(self) -> "Command":
        self._bytes[2] |= const.COMMAND_TIMER_UP
        return self

    @property
    def is_timer_up(self) -> bool:
        return bool(self._bytes[2] & const.COMMAND_TIMER_UP)

    def timer_down(self) -> "Command":
        self._bytes[2] |= const.COMMAND_TIMER_DOWN
        return self

    @property
    def is_timer_down(self) -> bool:
        return bool(self._bytes[2] & const.COMMAND_TIMER_DOWN)

    @property
    def bytes(self) -> bytes:
        return struct.pack(_COMMAND_STRUCT_FORMAT, *self._bytes)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Command):
            return False
        __value = cast(Command, __value)
        return self._bytes == __value._bytes
