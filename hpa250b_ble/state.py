import binascii
from dataclasses import dataclass, replace
import struct

from . import _LOGGER
from .const import PREAMBLE
from .enums import Preset, Backlight, VOCLight

# State structure:
# byte 1: <preamble>
# byte 2: 0 <turbo set> <allergy set> <general set> <germ set> <pollen set> <voc set> <power set>
# byte 3: <6-bit voc light spec> <2 bit backlight spec>
# byte 4: <pad byte>
# byte 5: <1 byte timer spec>
_STATE_STRUCT_FORMAT = ">BI14x"


class StateError(Exception):
    pass


@dataclass(frozen=True)
class State:
    is_on: bool
    preset: Preset | None
    backlight: Backlight | None
    voc_light: VOCLight | None
    timer: int | None

    @classmethod
    def empty(cls) -> "State":
        return State(False, None, None, None, None)

    @classmethod
    def from_bytes(cls, data: bytes) -> "State":
        _LOGGER.debug(
            f"constructing state from {len(data)} bytes: binascii.hexlify(data)"
        )

        try:
            _, state = struct.unpack(_STATE_STRUCT_FORMAT, data)
        except Exception as e:
            raise StateError(
                f"failed to deserialize state from {binascii.hexlify(data)}"
            ) from e

        is_on = _is_on_from_int(state)

        if not is_on:
            return State.empty()

        preset = _preset_from_int(state)
        if preset is None:
            raise ValueError("Could not determine preset from integer state", data)

        voc_light: VOCLight | None = None
        if preset in [Preset.AUTO_VOC_POLLEN, Preset.AUTO_VOC, Preset.AUTO_POLLEN]:
            voc_light = _voc_light_from_int(state)

        backlight = _backlight_from_int(state)
        timer = _timer_from_int(state)

        return State(is_on, preset, backlight, voc_light, timer)

    @property
    def bytes(self) -> bytes:
        data = 0
        data |= _is_on_to_int(self.is_on)
        data |= _preset_to_int(self.preset)
        data |= _voc_light_to_int(self.voc_light)
        data |= _backlight_to_int(self.backlight)
        data |= _timer_to_int(self.timer)

        return struct.pack(_STATE_STRUCT_FORMAT, PREAMBLE, data)

    def matches_desired_state(self, desired: "State") -> bool:
        return (
            self.is_on == desired.is_on
            and self.preset == desired.preset
            and self.backlight == desired.backlight
            and self.timer == desired.timer
        )

    def with_is_on(self, is_on: bool) -> "State":
        return replace(self, is_on=is_on)

    def with_preset(self, preset: Preset | None) -> "State":
        return replace(self, preset=preset)

    def with_backlight(self, backlight: Backlight) -> "State":
        return replace(self, preset=backlight)

    def with_timer(self, timer: int | None) -> "State":
        return replace(self, timer=timer)


def _is_on_from_int(n: int) -> bool:
    return bool(n & _is_on_to_int(True))


def _is_on_to_int(is_on: bool) -> int:
    if not is_on:
        return 0
    return 1 << 24


def _preset_from_int(n: int) -> Preset | None:
    if (n & (p := _preset_to_int(Preset.AUTO_VOC_POLLEN))) == p:
        return Preset.AUTO_VOC_POLLEN
    if (n & (p := _preset_to_int(Preset.AUTO_VOC))) == p:
        return Preset.AUTO_VOC
    if (n & (p := _preset_to_int(Preset.AUTO_POLLEN))) == p:
        return Preset.AUTO_POLLEN
    if (n & (p := _preset_to_int(Preset.GERM))) == p:
        return Preset.GERM
    if (n & (p := _preset_to_int(Preset.GENERAL))) == p:
        return Preset.GENERAL
    if (n & (p := _preset_to_int(Preset.ALLERGEN))) == p:
        return Preset.ALLERGEN
    if (n & (p := _preset_to_int(Preset.TURBO))) == p:
        return Preset.TURBO
    else:
        return None


def _preset_to_int(preset: Preset | None) -> int:
    return {
        None: 0,
        Preset.GERM: 1 << 27,
        Preset.GENERAL: 1 << 28,
        Preset.ALLERGEN: 1 << 29,
        Preset.TURBO: 1 << 30,
        Preset.AUTO_VOC: 1 << 25,
        Preset.AUTO_POLLEN: 1 << 26,
        Preset.AUTO_VOC_POLLEN: (1 << 25) | (1 << 26),
    }[preset]


def _voc_light_from_int(n: int) -> VOCLight:
    n = (n >> 16) & 0b11111100
    return {
        0: VOCLight.GREEN,
        4: VOCLight.AMBER,
        8: VOCLight.RED,
    }[n]


def _voc_light_to_int(voc_light: VOCLight | None) -> int:
    return {
        None: 0,
        VOCLight.GREEN: 0 << 16,
        VOCLight.AMBER: 4 << 16,
        VOCLight.RED: 8 << 16,
    }[voc_light]


def _backlight_from_int(n: int) -> Backlight:
    n = (n >> 16) & 0b00000011
    return {
        0: Backlight.ON,
        1: Backlight.DIM,
        2: Backlight.OFF,
    }[n]


def _backlight_to_int(backlight: Backlight | None) -> int:
    return {
        None: 0,
        Backlight.ON: 0 << 16,
        Backlight.DIM: 1 << 16,
        Backlight.OFF: 2 << 16,
    }[backlight]


def _timer_from_int(n: int) -> int | None:
    value = n & 0xFF
    if value == 0:
        return None
    return value


def _timer_to_int(timer: int | None) -> int:
    if timer is None:
        return 0
    return timer
