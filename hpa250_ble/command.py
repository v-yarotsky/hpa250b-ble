import struct
from typing import cast
from . import const

# Command structure:
# byte 0: <preamble>
# byte 1: 0 0 <toggle voc set> <turbo set> <allergen set> <general set> <germ set> <toggle power set>
# byte 2: 0 0 0 0 <toggle pollen set> <cycle light set> <timer down set> <timer up set>
# rest:   pad with 0x00
_COMMAND_STRUCT_FORMAT = ">BH17x"

TIMER_UP = 1 << 0
TIMER_DOWN = 1 << 1
LIGHT_CYCLE = 1 << 2
TOGGLE_POLLEN = 1 << 3
TOGGLE_POWER = 1 << 8
TOGGLE_GERM = 1 << 9
TOGGLE_GENERAL = 1 << 10
TOGGLE_ALLERGEN = 1 << 11
TOGGLE_TURBO = 1 << 12
TOGGLE_VOC = 1 << 13


class Command:
    command: int

    def __init__(self):
        self.command = 0

    def toggle_power(self) -> "Command":
        self.command |= TOGGLE_POWER
        return self

    @property
    def is_toggle_power(self) -> bool:
        return bool(self.command & TOGGLE_POWER)

    def toggle_germ(self) -> "Command":
        self.command |= TOGGLE_GERM
        return self

    @property
    def is_toggle_germ(self) -> bool:
        return bool(self.command & TOGGLE_GERM)

    def toggle_general(self) -> "Command":
        self.command |= TOGGLE_GENERAL
        return self

    @property
    def is_toggle_general(self) -> bool:
        return bool(self.command & TOGGLE_GENERAL)

    def toggle_allergen(self) -> "Command":
        self.command |= TOGGLE_ALLERGEN
        return self

    @property
    def is_toggle_allergen(self) -> bool:
        return bool(self.command & TOGGLE_ALLERGEN)

    def toggle_turbo(self) -> "Command":
        self.command |= TOGGLE_TURBO
        return self

    @property
    def is_toggle_turbo(self) -> bool:
        return bool(self.command & TOGGLE_TURBO)

    def toggle_auto_voc(self) -> "Command":
        self.command |= TOGGLE_VOC
        return self

    @property
    def is_toggle_auto_voc(self) -> bool:
        return bool(self.command & TOGGLE_VOC)

    def toggle_auto_pollen(self) -> "Command":
        self.command |= TOGGLE_POLLEN
        return self

    @property
    def is_toggle_auto_pollen(self) -> bool:
        return bool(self.command & TOGGLE_POLLEN)

    def cycle_light(self) -> "Command":
        self.command |= LIGHT_CYCLE
        return self

    @property
    def is_cycle_light(self) -> bool:
        return bool(self.command & LIGHT_CYCLE)

    def timer_up(self) -> "Command":
        self.command |= TIMER_UP
        return self

    @property
    def is_timer_up(self) -> bool:
        return bool(self.command & TIMER_UP)

    def timer_down(self) -> "Command":
        self.command |= TIMER_DOWN
        return self

    @property
    def is_timer_down(self) -> bool:
        return bool(self.command & TIMER_DOWN)

    @property
    def bytes(self) -> bytes:
        return struct.pack(_COMMAND_STRUCT_FORMAT, const.PREAMBLE, self.command)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Command):
            return False
        __value = cast(Command, __value)
        return self.command == __value.command
