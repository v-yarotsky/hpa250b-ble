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
_STATE_STRUCT_FORMAT = "xBBxB14x"


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
        _LOGGER.debug(f"constructing state from bytes: binascii.hexlify(data)")
        fan, lights, timer = struct.unpack(_STATE_STRUCT_FORMAT, data)

        if fan == const.STATE_OFF:
            return cls.empty()

        if timer == 0:
            timer = None

        backlight = Backlight.from_byte(lights)
        voc_light: Optional[VOCLight] = None

        assert fan & const.STATE_ON

        if fan & const.STATE_VOC_SET and fan & const.STATE_POLLEN_SET:
            preset = Preset.AUTO_VOC_POLLEN
            voc_light = VOCLight.from_byte(lights)
        elif fan & const.STATE_VOC_SET:
            preset = Preset.AUTO_VOC
            voc_light = VOCLight.from_byte(lights)
        elif fan & const.STATE_POLLEN_SET:
            preset = Preset.AUTO_POLLEN
            voc_light = VOCLight.from_byte(lights)
        elif fan & const.STATE_GERM:
            preset = Preset.GERM
        elif fan & const.STATE_GENERAL:
            preset = Preset.GENERAL
        elif fan & const.STATE_ALLERGEN:
            preset = Preset.ALLERGEN
        elif fan & const.STATE_TURBO:
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
