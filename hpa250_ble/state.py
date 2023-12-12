from dataclasses import dataclass
import logging
import struct
from typing import cast, Optional
from . import const, exc
from .enums import Preset, Backlight, VOCLight

_LOGGER = logging.getLogger(__name__)

# State structure:
# byte 1: <preamble>
# byte 2: 0 <turbo set> <allergy set> <general set> <germ set> <pollen set> <voc set> <power set>
# byte 3: <6-bit voc light spec> <2 bit backlight spec>
# byte 4: <pad byte>
# byte 5: <1 byte timer spec>
_STATE_STRUCT_FORMAT = ">cI14x"

IS_ON = 1 << 24
IS_VOC_SET = 1 << 25
IS_POLLEN_SET = 1 << 26
IS_GERM = 1 << 27
IS_GENERAL = 1 << 28
IS_ALLERGEN = 1 << 29
IS_TURBO = 1 << 30


@dataclass(frozen=True)
class State:
    is_on: bool
    preset: Optional[Preset]
    backlight: Optional[Backlight]
    voc_light: Optional[VOCLight]
    timer: Optional[int]

    @classmethod
    def empty(cls) -> "State":
        return State(False, None, None, None, None)

    @classmethod
    def from_bytes(cls, data: bytes) -> "State":
        _LOGGER.debug(
            f"constructing state from {len(data)} bytes: binascii.hexlify(data)"
        )
        _, state = struct.unpack(_STATE_STRUCT_FORMAT, data)

        voc_light_num = (state >> 16) & 0b11111100  # next 6 bits
        backlight_num = (state >> 16) & 0b00000011  # next 2 bits
        timer = state & 0xFF  # last 8 bits

        if not state & IS_ON:
            return cls.empty()

        if timer == 0:
            timer = None

        backlight = Backlight.from_int(backlight_num)
        voc_light: Optional[VOCLight] = None

        if state & IS_VOC_SET and state & IS_POLLEN_SET:
            preset = Preset.AUTO_VOC_POLLEN
            voc_light = VOCLight.from_int(voc_light_num)
        elif state & IS_VOC_SET:
            preset = Preset.AUTO_VOC
            voc_light = VOCLight.from_int(voc_light_num)
        elif state & IS_POLLEN_SET:
            preset = Preset.AUTO_POLLEN
            voc_light = VOCLight.from_int(voc_light_num)
        elif state & IS_GERM:
            preset = Preset.GERM
        elif state & IS_GENERAL:
            preset = Preset.GENERAL
        elif state & IS_ALLERGEN:
            preset = Preset.ALLERGEN
        elif state & IS_TURBO:
            preset = Preset.TURBO
        else:
            raise exc.StateError("Could not determine current preset", data)

        return State(True, preset, backlight, voc_light, timer)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, State):
            return False
        v = cast(State, __value)
        return (
            self.is_on == v.is_on
            and self.preset == v.preset
            and self.backlight == v.backlight
            and self.timer == v.timer
        )
